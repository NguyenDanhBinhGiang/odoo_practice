import odoo.exceptions
from odoo import models, fields, api


class SpendingConfig(models.Model):
    _name = 'spending.config'
    _inherit = 'single.line'

    name = fields.Text(default='The spending config')
    spending_limit_ids = fields.One2many('spending.limit', 'config_id', ondelete='cascade')
    currency_id = fields.Many2one('res.currency', 'Don vi tien te')

    @api.model
    def get_view(self):
        view_id = self.env.ref('purchase_inherit.spending_limit_form').id
        # maybe get_formview_action() will be better?
        return {
            'type': 'ir.actions.act_window',
            'name': 'test action server',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'spending.config',
            'res_id': self.search([])[0].id,
            'target': 'current',
        }
        pass


class SpendingLimit(models.Model):
    _name = 'spending.limit'
    _sql_constraints = [
        ('not_null_employee', 'UNIQUE(employee_id not null)', 'Employee can not be null'),
        ('unique_employee', 'UNIQUE(employee_id)', 'Duplicated employee'),
        ('check_limit', 'CHECK(limit>0)', 'Limit must be greater than 0'),
    ]

    config_id = fields.Many2one('spending.config')
    employee_id = fields.Many2one('hr.employee', string='Nhan vien')
    currency_id = fields.Many2one('res.currency', related='config_id.currency_id')
    limit = fields.Monetary('Han muc/don', currency_field='currency_id')

    @api.constrains('limit')
    def limit_constraint(self):
        for rec in self:
            if rec.limit < 0:
                raise odoo.exceptions.UserError('Limit must be greater than 0')
