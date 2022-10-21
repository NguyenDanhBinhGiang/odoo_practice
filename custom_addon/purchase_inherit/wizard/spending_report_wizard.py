from odoo import models, fields, api


class SpendingReportWizard(models.TransientModel):
    _name = 'spending.report.wizard'

    month = fields.Selection([(str(i), f"Thang {i}") for i in range(1, 13)],
                             default=False, index=True, string='Thang', required=True)

    department_ids = fields.Many2many('hr.department', 'spending_report_wizard_department_rel',
                                      string='Phong ban')
    report_ids = fields.One2many('spending.report', 'wizard_id', ondelete='cascade')

    name = fields.Char(compute='_compute_name')

    def _compute_name(self):
        for rec in self:
            rec.name = f"Bao cao chi tieu thang {rec.month}"

    # noinspection PyTypeChecker
    def show_report_btn(self):
        self.ensure_one()
        if self.department_ids:
            domain = [(5,)] + [(0, 0, {'department_id': x.id}) for x in self.department_ids]
        else:
            domain = [(5,)] + [(0, 0, {'department_id': x.id})
                               for x in self.env['hr.department'].sudo().search([])]
        self.update({
            'report_ids': domain
        })
        view_id = self.env.ref('purchase_inherit.spending_report_tree').id
        # maybe get_formview_action() will be better?
        return {
            'type': 'ir.actions.act_window',
            'name': 'show spending report',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'spending.report.wizard',
            'res_id': self.id,
            'target': 'current',
        }

    @api.model
    def get_view(self):
        view_id = self.env.ref('purchase_inherit.spending_report_form').id
        # maybe get_formview_action() will be better?
        return {
            'type': 'ir.actions.act_window',
            'name': 'Show spending report form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'spending.report.wizard',
            'target': 'new',
        }
        pass


class SpendingReport(models.TransientModel):
    _name = 'spending.report'

    wizard_id = fields.Many2one('spending.report.wizard', ondelete='cascade')
    department_id = fields.Many2one('hr.department',
                                    string='Ten phong ban')
    spending_limit = fields.Float(related='department_id.spending_limit')
    spending = fields.Float('Chi tieu thuc te', compute='_compute_department_spending', readonly=True)

    @api.depends('department_id')
    def _compute_department_spending(self):
        for rec in self:
            def is_correct_order(search_rec):
                return search_rec.department_id == rec.department_id \
                       and search_rec.date_order.month == int(rec.wizard_id.month)

            orders = self.env['purchase.order'].sudo().search(
                [('department_id', '!=', False), ('state', '=', 'purchase')]
            ).filtered(is_correct_order)
            rec.spending = sum([x.amount_total for x in orders])
