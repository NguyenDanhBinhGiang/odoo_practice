import datetime

import odoo.exceptions
from odoo import models, fields, api


class MonthlyReport(models.Model):
    _name = 'monthly.report'

    sale_report_ids = fields.One2many('monthly.sale.report.line', 'report_id', ondelete='cascade')
    purchase_report_ids = fields.One2many('monthly.purchase.report.line', 'report_id', ondelete='cascade')
    email_to = fields.Many2many('res.users')

    month = fields.Integer('Thang', required=True)
    year = fields.Integer('Nam', required=True)

    @api.constrains('month')
    def _month_constraint(self):
        for rec in self:
            if not 0 < int(rec.month) < 13:
                raise odoo.exceptions.ValidationError('Thang khong hop le')

    def monthly_cron_job(self):
        report = self.create_this_month_report()

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
            'email_from': 'nguyendanhbinhgiang@gmail.com',
            'email_to': 'nguyendanhbinhgiang@gmail.com',
        }

        mail_template = self.env.ref('report_crm_purchase.mail_template_cron_email_report')
        mail_template.send_mail(report.id, force_send=True, raise_exception=True, email_values=email_values)

    def create_report(self, month, year):
        domain = [('month', '=', month), ('year', '=', year)]
        recs = self.search(domain)

        # noinspection PyTypeChecker
        vals = {
            'month': month,
            'year': year,
            'email_to': [(5,)] + [(4, x.id)
                                  for x in self.env.ref('crm_sale_inherit.sale_department_manager').users[1]],
            'sale_report_ids': [(5,)] + [(0, 0, {'sale_team_id': x.id})
                                         for x in self.env['crm.team'].sudo().search([])],
            'purchase_report_ids': [(5,)] + [(0, 0, {'department_id': x.id})
                                             for x in self.env['hr.department'].sudo().search([])]
        }

        if len(recs) > 0:
            recs[0].update(vals)
            result = recs[0]
        else:
            result = self.create(vals)

        return result

    def create_last_month_report(self):
        today = datetime.date.today()
        return self.create_report(month=today.month - 1, year=today.year)

    def create_this_month_report(self):
        today = datetime.date.today()
        return self.create_report(month=today.month, year=today.year)


class MonthlySaleReport(models.Model):
    _name = 'monthly.sale.report.line'

    report_id = fields.Many2one('monthly.report', ondelete='cascade')
    sale_team_id = fields.Many2one('crm.team', 'Ten nhom ban hang')
    total_revenue = fields.Float('Doanh thu thuc te', compute='_compute_report', store=True)
    revenue_diff = fields.Float('Chenh lech doanh thu', compute='_compute_report', store=True)

    @api.depends('sale_team_id')
    def _compute_report(self):
        for rec in self:
            def filter_month(order):
                return order.date_order.month == int(rec.report_id.month)

            # set total revenue
            orders_revenue = self.env['sale.order'].sudo().search(
                [('team_id.id', '=', rec.sale_team_id.id), ('state', '=', 'sale')]
            ).filtered(filter_month).mapped('amount_total')
            rec.total_revenue = sum(orders_revenue)

            # set revenue dif
            expected_revenue = getattr(rec.sale_team_id, f"chi_tieu_doanh_so_thang_{rec.report_id.month}")
            rec.revenue_diff = rec.total_revenue - expected_revenue


class MonthlyPurchaseReport(models.Model):
    _name = 'monthly.purchase.report.line'

    report_id = fields.Many2one('monthly.report', ondelete='cascade')
    department_id = fields.Many2one('hr.department', 'Ten phong ban')
    total_spending = fields.Float('Chi tieu thuc te', compute='_compute_report', store=True)
    spending_diff = fields.Float('Chenh lech chi tieu', compute='_compute_report', store=True)

    @api.depends('department_id')
    def _compute_report(self):
        for rec in self:
            def filter_month(order):
                return order.date_approve.month == int(rec.report_id.month)

            orders_spending = self.env['purchase.order'].sudo().search(
                [('department_id', '=', rec.department_id.id), ('state', '=', 'purchase')]
            ).filtered(filter_month).mapped('amount_total')
            rec.total_spending = sum(orders_spending)

            spending_limit = rec.department_id.spending_limit
            rec.spending_diff = rec.total_spending - spending_limit
