from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Enrollment(models.Model):
    _name = 'lms.enrollment'
    _description = 'Student Course Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Enrollment Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    student_id = fields.Many2one('lms.student', string='Student', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True)
    enrollment_date = fields.Date(string='Enrollment Date', required=True, default=fields.Date.today)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], string='Payment Status', default='pending', tracking=True)
    total_fee = fields.Float(string='Total Fee', required=True)
    paid_amount = fields.Float(string='Paid Amount', default=0.0)
    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_remaining_amount', store=True)
    payment_plan_id = fields.Many2one('lms.payment.plan', string='Payment Plan')
    payment_ids = fields.One2many('lms.payment', 'enrollment_id', string='Payments')
    grade_ids = fields.One2many('lms.grade', 'enrollment_id', string='Grades')
    attendance_ids = fields.One2many('lms.attendance', 'enrollment_id', string='Attendance Records')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)
    schedule_id = fields.Many2one('lms.schedule', string='Schedule')
    teacher_assignment_id = fields.Many2one('lms.teacher.assignment', string='Teacher Assignment')

    @api.depends('total_fee', 'paid_amount')
    def _compute_remaining_amount(self):
        for enrollment in self:
            enrollment.remaining_amount = enrollment.total_fee - enrollment.paid_amount

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.enrollment') or 'New'
        return super(Enrollment, self).create(vals)

    def action_submit_for_approval(self):
        self.write({'state': 'pending'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Enrollment Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment',
            'view_mode': 'tree,form',
            'domain': [('enrollment_id', '=', self.id)],
            'context': {'default_enrollment_id': self.id},
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            'name': 'Enrollment Grades',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.grade',
            'view_mode': 'tree,form',
            'domain': [('enrollment_id', '=', self.id)],
            'context': {'default_enrollment_id': self.id},
        }

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'Enrollment Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('enrollment_id', '=', self.id)],
            'context': {'default_enrollment_id': self.id},
        }

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for enrollment in self:
            if enrollment.start_date > enrollment.end_date:
                raise ValidationError("End date must be after start date!")

    @api.constrains('student_id', 'course_id', 'academic_year_id', 'semester_id')
    def _check_duplicate_enrollment(self):
        for enrollment in self:
            if self.search_count([
                ('student_id', '=', enrollment.student_id.id),
                ('course_id', '=', enrollment.course_id.id),
                ('academic_year_id', '=', enrollment.academic_year_id.id),
                ('semester_id', '=', enrollment.semester_id.id),
                ('id', '!=', enrollment.id),
                ('state', 'not in', ['cancelled', 'rejected'])
            ]) > 0:
                raise ValidationError("Student is already enrolled in this course for the specified academic year and semester!")