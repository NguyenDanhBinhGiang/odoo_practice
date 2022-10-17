from odoo import models, fields, api


class DepartmentInherit(models.Model):
    _inherit = 'hr.department'

    spending_limit = fields.Float('Han muc chi tieu/thang')
