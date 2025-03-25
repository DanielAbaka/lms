from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Attendance(models.Model):
    _name = 'lms.attendance'
    _description = 'Student Attendance'
    _order = 'date desc, student_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Attendance Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    student_id = fields.Many2one('lms.student', string='Student', required=True)
    enrollment_id = fields.Many2one('lms.enrollment', string='Enrollment', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', related='enrollment_id.academic_year_id', store=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', related='enrollment_id.semester_id', store=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ], string='Status', required=True, default='present')
    notes = fields.Text(string='Notes')
    marked_by = fields.Many2one('res.users', string='Marked By', readonly=True, default=lambda self: self.env.user)
    session_type = fields.Selection([
        ('lecture', 'Lecture'),
        ('lab', 'Laboratory'),
        ('tutorial', 'Tutorial'),
        ('exam', 'Examination')
    ], string='Session Type', required=True, default='lecture')
    duration = fields.Float(string='Duration (hours)', default=1.0)
    location = fields.Char(string='Location')
    is_verified = fields.Boolean(string='Verified', default=False)
    verification_date = fields.Datetime(string='Verification Date', readonly=True)
    verified_by = fields.Many2one('res.users', string='Verified By', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.attendance') or 'New'
        return super(Attendance, self).create(vals)

    def action_verify(self):
        self.ensure_one()
        if not self.is_verified:
            self.write({
                'is_verified': True,
                'verification_date': fields.Datetime.now(),
                'verified_by': self.env.user.id
            })

    def action_unverify(self):
        self.ensure_one()
        if self.is_verified:
            self.write({
                'is_verified': False,
                'verification_date': False,
                'verified_by': False
            })

    def action_mark_all_present(self):
        for record in self:
            record.status = 'present'

    def action_mark_all_absent(self):
        for record in self:
            record.status = 'absent'

    def action_mark_all_late(self):
        for record in self:
            record.status = 'late'

    def action_mark_all_excused(self):
        for record in self:
            record.status = 'excused'

    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.context_today(self):
                raise ValidationError("Attendance date cannot be in the future!")

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError("Duration must be greater than 0!")

    @api.constrains('enrollment_id', 'student_id')
    def _check_enrollment_student(self):
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError("Student must match the enrollment record!") 