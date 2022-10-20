import datetime

from odoo import models, fields, api


class CrmLeadReportWizard(models.TransientModel):
    _name = 'crm.team.report.wizard'

    month = fields.Selection([(str(i), f'Thang {i}') for i in range(1, 13)], string='Thang', required=True, )
    sale_team_ids = fields.Many2many('crm.team', string='Nhom ban hang')
    team_report_ids = fields.One2many('crm.team.report', 'wizard_id')

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
    real_revenue = fields.Float(compute='_compute_report', string='Doanh thu thuc te')
    expected_revenue = fields.Float(compute='_compute_report', string='Chi tieu doanh thu')

    @api.depends('team_id')
    def _compute_report(self):
        for rec in self:
            def filter_month(f_rec):
                return f_rec.date_order.month == int(rec.wizard_id.month)
            rec.expected_revenue = getattr(rec.team_id, f"chi_tieu_doanh_so_thang_{rec.wizard_id.month}")
            orders_revenue = self.env['sale.order'].search(
                [('team_id.id', '=', rec.team_id.id), ('state', '=', 'sale')]
            ).filtered(filter_month).mapped('amount_total')
            rec.real_revenue = sum(orders_revenue)
