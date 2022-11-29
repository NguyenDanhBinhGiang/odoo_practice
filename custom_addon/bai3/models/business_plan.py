from typing import List

import odoo.exceptions
from odoo import models, fields, api


# noinspection SpellCheckingInspection
class BusinessPlan(models.Model):
    _name = 'business.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _sql_constraints = [
        ('unique_sale_order_id', 'UNIQUE(sale_order_id)', 'sale_order_id must be unique')
    ]

    state = fields.Selection([
        ('draft', 'New'),
        ('sent', 'Waiting for confirmation'),
        ('approved', 'Approved'),
        ('declined', 'Declined')],
        string='Status', readonly=True, index=True, default='draft', compute='_compute_state', store=True)
    sale_order_id = fields.Many2one('sale.order', required=True, readonly=True, ondelete='restrict')
    name = fields.Char(compute='_compute_name', store=True)
    detail = fields.Text('Business info', required=True)
    approvals_id = fields.One2many('approval', 'business_plan_id', ondelete='cascade')

    # rec_name = fields.Text(compute='_compute_rec_name', invisible=True)
    """Computed fields for form attribute"""
    readonly_state = fields.Boolean(compute='_compute_readonly', invisible=True, default=False)
    sent_btn_visible = fields.Boolean(compute='_compute_sent_btn_visible', invisible=True, default=True)

    def _compute_sent_btn_visible(self):
        for record in self:
            record.sent_btn_visible = self.env.user == record.create_uid

    @api.constrains('approvals_id', 'state')
    def constrain_approval(self):
        for record in self:
            if len(record.approvals_id) < 1 and self.state in ('sent', 'approved'):
                raise odoo.exceptions.UserError('Approve list cannot be empty')

    @api.depends('name', 'sale_order_id.name')
    def _compute_name(self):
        for record in self:
            record.name = f"Sale order/{record.sale_order_id.name}"

    @api.depends('state')
    def _compute_readonly(self):
        for record in self:
            record.readonly_state = record.state not in ['draft', 'declined']
            # or self.env.user.id == record.create_uid

    @api.depends('approvals_id.approve_state')
    def _compute_state(self):
        for record in self:
            if record.state != 'sent':
                return
            if record.approvals_id:
                approve_result = [x.approve_state == 'approved' for x in record.approvals_id]
                decline_result = [x.approve_state == 'declined' for x in record.approvals_id]
                if any(decline_result):
                    record.state = 'declined'
                    self.sudo().message_post(body=f'Business plan \"{record.name}\" has been declined',
                                             partner_ids=[record.create_uid.partner_id.id],
                                             message_type='notification')
                elif all(approve_result):
                    record.state = 'approved'
                    self.sudo().message_post(body=f'Business plan \"{record.name}\" has been approved',
                                             partner_ids=[record.create_uid.partner_id.id],
                                             message_type='notification')

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'sent'),
                   ('draft', 'approved'),
                   ('draft', 'declined'),
                   ('sent', 'approved'),
                   ('sent', 'declined'),
                   ('declined', 'sent')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        self.ensure_one()
        if self.is_allowed_transition(self.state, new_state):
            self.state = new_state
        else:
            raise odoo.exceptions.UserError(f"You can't change state from {self.state} to {new_state}")

    def make_sent(self):
        self.ensure_one()
        for a in self.approvals_id:
            a.sudo().make_draft()
        message_list = self.approvals_id.mapped('user_id.partner_id.id')
        self.sudo().message_post(body='Business plan need approval',
                                 partner_ids=message_list,
                                 message_type='notification')
        self.change_state('sent')
        pass

    def delete_all_approvals(self):
        for rec in self:
            # approve_id = rec.approvals_id.mapped('id')
            # domain = [(2, a_id) for a_id in approve_id]

            # if the one2many relation have ondelete='cascade', then unlinked records will be deleted.
            domain = [(5,)]
            rec.update({
                'approvals_id': domain
            })

    def assign_approver(self, approvers):
        """
        Assign a list of user to approve the plans
        :param approvers: a list of res.users to assign
        """
        for rec in self:
            domain = [
                (0, 0, {'user_id': approver.id})
                for approver in approvers
            ]
            rec.update({
                'approvals_id': domain
            })

    def assign_default_approval(self):
        quanly_users = self.env.ref('bai3.default_management_department').member_ids.mapped('user_id')
        self.assign_approver(quanly_users)

    def reassign_to_sale_users(self):
        self.delete_all_approvals()
        sale_users = self.env.ref('bai3.default_sale_department').member_ids.mapped('user_id')
        self.assign_approver(sale_users)

    def send_email_action(self):
        for appr in self.approvals_id:
            # TODO: check approval status, don't send email again
            email_values = {
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
                'email_from': 'nguyendanhbinhgiang@gmail.com',
                'email_to': appr.user_id.partner_id.email,
            }

            mail_template = self.env.ref('bai3.mail_template_approval_email')
            mail_template.send_mail(appr.id, force_send=True, raise_exception=True, email_values=email_values)

    @api.model
    def create(self, vals_list):
        new_plan = super(BusinessPlan, self).create(vals_list=vals_list)
        if not new_plan.approvals_id:
            new_plan.assign_default_approval()
        return new_plan

    # @api.model
    def write(self, vals):
        if self.readonly_state:
            raise odoo.exceptions.UserError('You can not edit project detail after sending it')

        return super(BusinessPlan, self).write(vals)
