import datetime

from odoo import models, fields, api


class CrmLeadReportWizard(models.TransientModel):
    _name = 'crm.lead.report.wizard'

    name = fields.Char(compute='_compute_name')
    month = fields.Selection([(str(i), f'Thang {i}') for i in range(1, 13)], string='Thang', required=True,
                             default=str(datetime.datetime.now().month), )
    sale_team_ids = fields.Many2many('crm.team', string='Nhom ban hang')

    def _compute_name(self):
        for rec in self:
            rec.name = f"Bao cao thang {rec.month}"

    @api.model
    def get_view(self):

        view_id = self.env.ref('crm_sale_inherit.crm_report_form').id
        # maybe get_formview_action() will be better?
        return {
            'type': 'ir.actions.act_window',
            # 'name': 'Show spending report form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'crm.lead.report.wizard',
            'target': 'new',
        }

    def show_report_btn(self):
        self.ensure_one()
        assert self.month, 'Month is required!'
        view_id = self.env.ref('crm_sale_inherit.crm_lead_report_view').id
        domain = [('month_open', '=', self.month), ]
        if len(self.sale_team_ids) > 0:
            domain += [('team_id.id', 'in', self.sale_team_ids.mapped('id')), ]
        return {
            'type': 'ir.actions.act_window',
            # 'name': 'Show spending report form',
            'view_mode': 'tree',
            'view_id': view_id,
            'res_model': 'crm.lead',
            'target': 'current',
            'domain': domain,
            'context': {'search_default_saleschannel': 1, 'search_default_salesperson': 2, },
        }
