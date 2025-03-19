from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LMSEnrollment(models.Model):
    _name = 'lms.enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # for chatter & activity
    _description = 'Course Enrollment'

    student_id = fields.Many2one(
        'res.users',
        string="Student",
        domain=[('is_student', '=', True)],
        required=True
    )
    course_id = fields.Many2many(
        'slide.channel',
        string="Courses",
        required=True
    )
    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.today,
        required=True
    )
    payment_status = fields.Selection([
            ('pending', 'Pending'),
            ('installment_1', 'Installment 1 Paid'),
            ('installment_2', 'Installment 2 Paid'),
            ('paid', 'Fully Paid')
        ],
        string="Payment Status",
        default='pending',
        tracking=True
    )
    total_cost = fields.Float(string="Total Cost", required=True)
    remaining_balance = fields.Float(
        string="Remaining Balance",
        compute="_compute_remaining_balance",
        store=True
    )

    @api.depends('payment_status', 'total_cost')
    def _compute_remaining_balance(self):
        for record in self:
            if record.payment_status == 'pending':
                record.remaining_balance = record.total_cost
            elif record.payment_status == 'installment_1':
                record.remaining_balance = record.total_cost * 2 / 3
            elif record.payment_status == 'installment_2':
                record.remaining_balance = record.total_cost / 3
            else:  # 'paid'
                record.remaining_balance = 0

    def make_payment(self):
        """Move payment_status through pending -> installment_1 -> installment_2 -> paid."""
        if self.payment_status == 'pending':
            self.payment_status = 'installment_1'
        elif self.payment_status == 'installment_1':
            self.payment_status = 'installment_2'
        elif self.payment_status == 'installment_2':
            self.payment_status = 'paid'