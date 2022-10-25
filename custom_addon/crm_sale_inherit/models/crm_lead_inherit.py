import odoo.exceptions
from odoo import models, fields, api


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    _sql_constraints = [('min_revenue_check', 'CHECK(min_revenue>0)', 'Doanh thu toi thieu phai >0')]

    min_revenue = fields.Monetary('Doanh thu toi thieu', currency_field='company_currency')
    month_open = fields.Integer(compute='_compute_month_opened', store=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
        override read_group to allow computed field sale_amount_total to have sum in group by search view.
        store=True works too btw.
        """
        res = super(CrmLeadInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                     orderby=orderby, lazy=lazy)
        if 'sale_amount_total' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    sum_total_real_income = 0.0
                    for record in lines:
                        sum_total_real_income += record.sale_amount_total
                    line['sale_amount_total'] = sum_total_real_income

        return res

    @api.depends('date_open')
    def _compute_month_opened(self):
        for rec in self:
            if rec.date_open:
                rec.month_open = rec.date_open.month
            else:
                rec.month_open = False

    # noinspection PyUnresolvedReferences
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
