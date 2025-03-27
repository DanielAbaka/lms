from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LMSPayment(models.Model):
    _name = 'lms.payment'
    _description = 'LMS Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, student_id'

    name = fields.Char(string='Payment Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    student_id = fields.Many2one('res.users', string='Student', required=True, domain=[('is_student','=',True)])
    enrollment_id = fields.Many2one('lms.enrollment', string='Enrollment', required=True)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    course_id = fields.Many2one('slide.channel', string='Course', related='enrollment_id.course_id', store=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', related='enrollment_id.academic_year_id', store=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', related='enrollment_id.semester_id', store=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Amount', required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], string='Payment Status', compute='_compute_payment_status', store=True)
    notes = fields.Text(string='Notes')
    receipt_number = fields.Char(string='Receipt Number', copy=False)
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    received_by = fields.Many2one('res.users', string='Received By', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.payment') or 'New'
        return super(LMSPayment, self).create(vals)

    def action_confirm_payment(self):
        self.ensure_one()
        if not self.payment_date:
            self.write({
                'state': 'completed',
                'payment_date': fields.Datetime.now(),
                'received_by': self.env.user.id
            })
            # Update enrollment payment status
            self.enrollment_id.paid_amount += self.amount
            if self.enrollment_id.paid_amount >= self.enrollment_id.total_fee:
                self.enrollment_id.payment_status = 'paid'
            elif self.enrollment_id.paid_amount > 0:
                self.enrollment_id.payment_status = 'partial'

    def action_cancel_payment(self):
        self.ensure_one()
        if self.state != 'completed':
            self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.write({'state': 'draft'})

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Amount must be greater than 0!")

    @api.constrains('enrollment_id', 'student_id')
    def _check_enrollment_student(self):
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError("Student must match the enrollment record!")

    @api.constrains('amount', 'enrollment_id')
    def _check_payment_amount(self):
        for record in self:
            if record.state == 'completed':
                total_paid = record.enrollment_id.paid_amount - record.amount
                if total_paid + record.amount > record.enrollment_id.total_fee:
                    raise ValidationError("Payment amount exceeds the total fee!")

    @api.depends('state', 'amount', 'enrollment_id.paid_amount', 'enrollment_id.total_fee')
    def _compute_payment_status(self):
        for record in self:
            if record.state == 'completed':
                total_paid = record.enrollment_id.paid_amount
                if total_paid >= record.enrollment_id.total_fee:
                    record.payment_status = 'paid'
                elif total_paid > 0:
                    record.payment_status = 'partial'
                else:
                    record.payment_status = 'unpaid'
            else:
                record.payment_status = 'unpaid'