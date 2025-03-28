from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PaymentPlan(models.Model):
    _name = 'lms.payment.plan'
    _description = 'Payment Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', copy=False)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    enrollment_id = fields.Many2one('lms.enrollment', string='Enrollment')
    student_id = fields.Many2one('res.users', string='Student', related='enrollment_id.student_id', store=True)
    description = fields.Text(string='Description')
    total_amount = fields.Float(string='Total Amount', required=True)
    paid_amount = fields.Float(string='Paid Amount', default=0.0)
    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_remaining_amount', store=True)
    number_of_installments = fields.Integer(string='Number of Installments', required=True)
    installment_amount = fields.Float(string='Installment Amount', compute='_compute_installment_amount', store=True)
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency', required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method')
    due_date = fields.Date(string='Next Due Date')
    notes = fields.Text(string='Notes')
    payment_ids = fields.One2many('lms.payment', 'payment_plan_id', string='Payments')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    @api.depends('total_amount', 'paid_amount')
    def _compute_remaining_amount(self):
        for plan in self:
            plan.remaining_amount = plan.total_amount - plan.paid_amount

    @api.depends('total_amount', 'number_of_installments')
    def _compute_installment_amount(self):
        for plan in self:
            if plan.number_of_installments > 0:
                plan.installment_amount = plan.total_amount / plan.number_of_installments
            else:
                plan.installment_amount = 0.0

    @api.constrains('number_of_installments')
    def _check_installments(self):
        for plan in self:
            if plan.number_of_installments < 1:
                raise ValidationError("Number of installments must be at least 1!")

    @api.constrains('total_amount')
    def _check_amount(self):
        for plan in self:
            if plan.total_amount <= 0:
                raise ValidationError("Total amount must be greater than 0!")

    def action_confirm(self):
        self.write({'state': 'pending'})

    def action_mark_paid(self):
        self.write({'state': 'paid'})

    def action_archive(self):
        self.write({'state': 'archived'})