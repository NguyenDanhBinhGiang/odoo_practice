import odoo.exceptions
from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    _sql_constraints = [('min_income_check', 'CHECK(min_income>0)', 'Doanh thu toi thieu phai >0')]

    min_income = fields.Float('Doanh thu toi thieu')

    def action_set_lost(self, **kwargs):
        if self.priority == '3':
            if not self.user_has_groups('crm_sale_inherit.sale_department_manager'):
                raise odoo.exceptions.UserError('Chi truong phong moi co the mark lost khi priority la cao nhat')

        super(CrmLeadInherit, self).action_set_lost(**kwargs)

    def write(self, vals):
        super(CrmLeadInherit, self).write(vals)

    @api.constrains('user_id')
    def assign_constraint(self):
        if not self.user_id.sale_team_id == self.env.user.sale_team_id:
            raise odoo.exceptions.ValidationError('You can only assign lead to other member of your sale team')

    def write(self, vals):
        if self.quotation_count > 0 and 'min_income' in vals:
            raise odoo.exceptions.UserError('Ban ko the edit tiem nang khi quotation_count > 0')
        super(CrmLeadInherit, self).write(vals)

