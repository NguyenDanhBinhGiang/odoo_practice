from odoo import models, fields, api


class DepartmentInherit(models.Model):
    _inherit = 'hr.department'

    currency_id = fields.Many2one("res.currency", string="Currency")
    spending_limit = fields.Monetary('Han muc chi tieu/thang', currency_field='currency_id')
