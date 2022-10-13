from odoo import models, fields, api


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    department = fields.Many2one('hr.department', string='Phong ban')
