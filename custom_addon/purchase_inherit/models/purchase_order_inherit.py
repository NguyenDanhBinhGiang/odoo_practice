import datetime
import odoo.exceptions
from odoo import models, fields, registry, api, SUPERUSER_ID


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    department_id = fields.Many2one('hr.department', string='Phong ban')

    def over_spending_limit(self):
        self.ensure_one()

        def correct_user(rec):
            return rec.employee_id.user_id.id == self.env.user.id

        spending_limit = self.env['spending.limit'].sudo().search([]).filtered(correct_user).limit
        return self.amount_total > spending_limit

    def button_confirm(self):
        for rec in self:
            if not rec.over_spending_limit() or self.user_has_groups('purchase_inherit.invoice_employee'):
                super(PurchaseOrderInherit, self).button_confirm()
            else:
                rec.create_activity()
                # partner_list = self.env.ref('purchase_inherit.invoice_employee').mapped('users.partner_id.id')
                # self.sudo().message_post(body=f'Purchase order need confirm',
                #                          partner_ids=partner_list,
                #                          message_type='notification')

                # self.env.cr.commit()
                raise odoo.exceptions.UserError('Ban da vuot qua han muc quy dinh, hay doi ke toan xac nhan')

                # return {
                #     'warning': {
                #         'title': "Warning",
                #         'message': "Ban da vuot qua han muc quy dinh, hay doi ke toan xac nhan",
                #     }
                # }

    def create_activity(self):
        self.ensure_one()
        # db_name = registry_get(self.env['ir.model'].sudo().search([('model', '=', 'mail.activity')]).name)
        # with registry().cursor() as cr:
        #     env = api.Environment(cr, SUPERUSER_ID, {})
        todos = [{
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'purchase.order')]).id,
            'user_id': kt.id,
            'summary': 'can confirm',
            'note': 'Can nhan vien ke toan confirm',
            'activity_type_id': 4,
            'date_deadline': datetime.date.today(),
        } for kt in self.env.ref('purchase_inherit.invoice_employee').users]

        for todo in todos:
            self.env['mail.activity'].sudo().create(todo)
            self.env.cr.commit()
