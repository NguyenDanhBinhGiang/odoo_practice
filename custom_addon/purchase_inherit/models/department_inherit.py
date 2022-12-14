from odoo import models, fields


class DepartmentInherit(models.Model):
    _inherit = 'hr.department'

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    spending_limit = fields.Monetary('Han muc chi tieu/thang', currency_field='currency_id')
