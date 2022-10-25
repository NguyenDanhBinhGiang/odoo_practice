import odoo.exceptions
from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    _sql_constraints = [('min_revenue_check', 'CHECK(min_revenue>0)', 'Doanh thu toi thieu phai >0')]

    # FIXME: add currency
    # TODO: related, count
    min_revenue = fields.Float('Doanh thu toi thieu')
    total_real_income = fields.Float('Doanh thu thuc te', compute='_compute_total_real_income')
    month_open = fields.Integer(compute='_compute_month_opened', store=True)

    @api.depends('date_open')
    def _compute_month_opened(self):
        for rec in self:
            if rec.date_open:
                rec.month_open = rec.date_open.month
            else:
                rec.month_open = False

    def _compute_total_real_income(self):
        """Compute total income from sale ORDER"""
        # FIXME: wrong values
        for rec in self:
            orders_income = [x.amount_total for x in rec.order_ids if x.state == 'sale']
            rec.total_real_income = sum(orders_income)

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
            if not self.user_has_groups('crm_sale_inherit.sale_department_manager'):
                raise odoo.exceptions.UserError('You can only assign lead to other member of your sale team')

    def write(self, vals):
        if self.quotation_count > 0 and 'min_revenue' in vals:
            raise odoo.exceptions.UserError('Ban ko the edit tiem nang khi quotation_count > 0')
        super(CrmLeadInherit, self).write(vals)
