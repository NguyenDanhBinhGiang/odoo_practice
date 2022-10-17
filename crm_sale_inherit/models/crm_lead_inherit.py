import odoo.exceptions
from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    def action_set_lost(self, **kwargs):
        if self.priority == '3':
            if not self.user_has_groups('crm_sale_inherit.sale_department_manager'):
                raise odoo.exceptions.UserError('Chi truong phong moi co the mark lost khi priority la cao nhat')

        super(CrmLeadInherit, self).action_set_lost(**kwargs)
