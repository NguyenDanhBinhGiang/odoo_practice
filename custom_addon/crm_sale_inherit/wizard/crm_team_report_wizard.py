import datetime

from odoo import models, fields, api


class CrmLeadReportWizard(models.TransientModel):
    _name = 'crm.team.report.wizard'

    def default_currency(self):
        return self.env.company.currency_id.id

    month = fields.Selection([(str(i), f'Thang {i}') for i in range(1, 13)], string='Thang',
                             default=str(datetime.date.today().month), required=True, )
    sale_team_ids = fields.Many2many('crm.team', string='Nhom ban hang')
    team_report_ids = fields.One2many('crm.team.report', 'wizard_id')
    currency_id = fields.Many2one('res.currency', default=default_currency)
    name = fields.Char(compute='_compute_name')

    @api.depends('month')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Bao cao danh gia chi tieu thang {rec.month}"

    @api.model
    def get_view(self):
        view_id = self.env.ref('crm_sale_inherit.crm_team_report_form').id
        # maybe get_formview_action() will be better?
        return {
            'type': 'ir.actions.act_window',
            # 'name': 'Show spending report form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'crm.team.report.wizard',
            'target': 'new',
        }

    def show_report_btn(self):
        self.ensure_one()
        assert self.month, 'Month is required!'
        if self.sale_team_ids:
            domain = [(0, 0, {'team_id': x.id}) for x in self.sale_team_ids]
        else:
            domain = [(0, 0, {'team_id': x.id})
                      for x in self.env['crm.team'].sudo().search([])]
        self.update({
            'team_report_ids': domain
        })

        view_id = self.env.ref('crm_sale_inherit.team_report_tree').id
        # noinspection PyUnresolvedReferences
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bao cao chi tiet',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'crm.team.report.wizard',
            'res_id': self.id,
            'target': 'current',
        }


class CrmTeamReport(models.TransientModel):
    _name = 'crm.team.report'

    wizard_id = fields.Many2one('crm.team.report.wizard', invisible=True)
    team_id = fields.Many2one('crm.team', string='Nhom ban hang')
    report_currency_id = fields.Many2one(related='wizard_id.currency_id')
    real_revenue = fields.Monetary(compute='_compute_report', string='Doanh thu thuc te',
                                   currency_field='report_currency_id')
    expected_revenue = fields.Monetary(compute='_compute_report', string='Chi tieu doanh thu',
                                       currency_field='report_currency_id')

    # noinspection PyProtectedMember
    @api.depends('team_id')
    def _compute_report(self):
        for rec in self:
            rec.expected_revenue = getattr(rec.team_id, f"chi_tieu_doanh_so_thang_{rec.wizard_id.month}")
            rec.expected_revenue = rec.team_id.expected_revenue_currency_id._convert(
                rec.expected_revenue, rec.report_currency_id,
                rec.team_id.company_id or self.env.user.company_id,
                datetime.date.today().replace(month=int(rec.wizard_id.month))
            )

            # Get orders
            def filter_month(f_rec):
                return f_rec.date_open.month == int(rec.wizard_id.month)

            orders = self.env['crm.lead'].search(
                [('team_id.id', '=', rec.team_id.id)]
            ).filtered(filter_month).mapped('order_ids')
            orders = [x for x in orders if x.state not in ('draft', 'sent', 'cancel')]

            # calculates total revenue in one currency
            total_revenue = 0.0
            for order in orders:
                total_revenue += order.currency_id._convert(
                    order.amount_untaxed, rec.report_currency_id, order.company_id,
                    order.date_order or fields.Date.today())

            rec.real_revenue = total_revenue
