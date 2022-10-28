import datetime

import odoo.exceptions
from odoo import models, fields, api


class MonthlyReport(models.Model):
    _name = 'monthly.report'

    sale_report_ids = fields.One2many('monthly.sale.report.line', 'report_id', ondelete='cascade')
    purchase_report_ids = fields.One2many('monthly.purchase.report.line', 'report_id', ondelete='cascade')
    email_to = fields.Many2many('res.users')

    def default_currency(self):
        return self.env.user.company_id.currency_id

    name = fields.Char(compute='_compute_name')
    currency_id = fields.Many2one('res.currency', default=default_currency)

    month = fields.Integer('Thang', required=True)
    year = fields.Integer('Nam', required=True)

    @api.depends('month', 'year')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Bao cao thang {rec.month} nam {rec.year}"

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
    currency_id = fields.Many2one('res.currency', related='report_id.currency_id')
    total_revenue = fields.Monetary('Doanh thu thuc te', currency_field='currency_id',
                                    compute='_compute_report', store=True)
    revenue_diff = fields.Monetary('Chenh lech doanh thu', currency_field='currency_id',
                                   compute='_compute_report', store=True)

    # noinspection PyProtectedMember
    @api.depends('sale_team_id')
    def _compute_report(self):
        for rec in self:
            def filter_month(order):
                return order.date_order.month == int(rec.report_id.month)

            # set total revenue
            orders = self.env['sale.order'].sudo().search(
                [('team_id.id', '=', rec.sale_team_id.id), ('state', 'in', ('sale', 'done'))]
            ).filtered(filter_month)
            revenues = [order.currency_id._convert(
                order.amount_untaxed, rec.currency_id, order.company_id, order.date_order or fields.Date.today())
                for order in orders]
            rec.total_revenue = sum(revenues)

            # set revenue diff
            expected_revenue = getattr(rec.sale_team_id, f"chi_tieu_doanh_so_thang_{rec.report_id.month}")
            expected_revenue = rec.sale_team_id.expected_revenue_currency_id._convert(
                expected_revenue, rec.currency_id,
                rec.sale_team_id.company_id or self.env.user.company_id,
                datetime.date.today()
            )
            rec.revenue_diff = rec.total_revenue - expected_revenue


class MonthlyPurchaseReport(models.Model):
    _name = 'monthly.purchase.report.line'

    report_id = fields.Many2one('monthly.report', ondelete='cascade')
    department_id = fields.Many2one('hr.department', 'Ten phong ban')
    currency_id = fields.Many2one('res.currency', related='report_id.currency_id')
    total_spending = fields.Monetary('Chi tieu thuc te', currency_field='currency_id',
                                     compute='_compute_report', store=True)
    spending_diff = fields.Monetary('Chenh lech chi tieu', currency_field='currency_id',
                                    compute='_compute_report', store=True)

    # noinspection PyProtectedMember
    @api.depends('department_id')
    def _compute_report(self):
        for rec in self:
            def filter_month(order):
                return order.date_approve.month == int(rec.report_id.month)

            orders = self.env['purchase.order'].sudo().search(
                [('department_id', '=', rec.department_id.id), ('state', 'in', ('purchase', 'done'))]
            ).filtered(filter_month)
            spending = [order.currency_id._convert(
                order.amount_untaxed, rec.currency_id, order.company_id, order.date_order or fields.Date.today())
                for order in orders]
            rec.total_spending = sum(spending)

            spending_limit = rec.department_id.currency_id._convert(
                rec.department_id.spending_limit, rec.currency_id, rec.department_id.company_id, fields.Date.today()
            )
            rec.spending_diff = rec.total_spending - spending_limit
