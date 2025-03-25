from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PaymentPlan(models.Model):
    _name = 'lms.payment.plan'
    _description = 'Payment Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    description = fields.Text(string='Description')
    total_amount = fields.Float(string='Total Amount', required=True)
    number_of_installments = fields.Integer(string='Number of Installments', required=True)
    installment_amount = fields.Float(string='Installment Amount', compute='_compute_installment_amount', store=True)
    payment_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semiannual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], string='Payment Frequency', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

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

    def action_activate(self):
        self.write({'state': 'active'})

    def action_archive(self):
        self.write({'state': 'archived'}) 