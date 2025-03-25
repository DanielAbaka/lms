from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class Student(models.Model):
    _inherit = 'res.users'
    _description = 'Student'

    is_student = fields.Boolean(string='Is Student', default=True)
    student_id = fields.Char(string='Student ID', required=True, copy=False)
    date_of_birth = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    emergency_contact = fields.Char(string='Emergency Contact')
    emergency_phone = fields.Char(string='Emergency Phone')
    blood_group = fields.Char(string='Blood Group')
    medical_conditions = fields.Text(string='Medical Conditions')
    academic_year = fields.Many2one('lms.academic.year', string='Current Academic Year')
    semester = fields.Many2one('lms.semester', string='Current Semester')
    major = fields.Char(string='Major')
    minor = fields.Char(string='Minor')
    expected_graduation = fields.Date(string='Expected Graduation')
    gpa = fields.Float(string='GPA', compute='_compute_gpa', store=True)
    credits_completed = fields.Integer(string='Credits Completed', compute='_compute_credits', store=True)
    credits_remaining = fields.Integer(string='Credits Remaining', compute='_compute_credits', store=True)
    total_credits = fields.Integer(string='Total Credits Required', default=120)
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_stats', store=True)
    active_enrollment_count = fields.Integer(string='Active Enrollments', compute='_compute_enrollment_stats', store=True)
    attendance_rate = fields.Float(string='Attendance Rate', compute='_compute_attendance_stats', store=True)
    average_grade = fields.Float(string='Average Grade', compute='_compute_grade_stats', store=True)
    pending_payments = fields.Float(string='Pending Payments', compute='_compute_payment_stats', store=True)
    enrollment_ids = fields.One2many('lms.enrollment', 'student_id', string='Enrollments')
    attendance_ids = fields.One2many('lms.attendance', 'student_id', string='Attendance Records')
    grade_ids = fields.One2many('lms.grade', 'student_id', string='Grades')
    payment_ids = fields.One2many('lms.payment', 'student_id', string='Payments')
    document_ids = fields.One2many('lms.document', 'student_id', string='Documents')
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages', domain=[('model', '=', 'res.users')])

    @api.depends('grade_ids.grade')
    def _compute_gpa(self):
        for student in self:
            grades = student.grade_ids.filtered(lambda g: g.grade)
            if grades:
                total_points = sum(grades.mapped('grade'))
                student.gpa = total_points / len(grades)
            else:
                student.gpa = 0.0

    @api.depends('grade_ids.credits')
    def _compute_credits(self):
        for student in self:
            completed_credits = sum(student.grade_ids.filtered(lambda g: g.grade >= 60).mapped('credits'))
            student.credits_completed = completed_credits
            student.credits_remaining = student.total_credits - completed_credits

    @api.depends('enrollment_ids')
    def _compute_enrollment_stats(self):
        for student in self:
            student.enrollment_count = len(student.enrollment_ids)
            student.active_enrollment_count = len(student.enrollment_ids.filtered(lambda e: e.state == 'approved'))

    @api.depends('attendance_ids')
    def _compute_attendance_stats(self):
        for student in self:
            attendances = student.attendance_ids.filtered(lambda a: a.date >= fields.Date.today() - timedelta(days=30))
            if attendances:
                present_count = len(attendances.filtered(lambda a: a.status == 'present'))
                student.attendance_rate = (present_count / len(attendances)) * 100
            else:
                student.attendance_rate = 0.0

    @api.depends('grade_ids.grade')
    def _compute_grade_stats(self):
        for student in self:
            grades = student.grade_ids.filtered(lambda g: g.grade)
            if grades:
                student.average_grade = sum(grades.mapped('grade')) / len(grades)
            else:
                student.average_grade = 0.0

    @api.depends('payment_ids')
    def _compute_payment_stats(self):
        for student in self:
            student.pending_payments = sum(student.payment_ids.filtered(lambda p: p.state == 'pending').mapped('amount'))

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': 'My Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'My Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            'name': 'My Grades',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.grade',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'My Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': 'My Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.document',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_enroll_course(self):
        self.ensure_one()
        return {
            'name': 'Enroll in Course',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_student_id': self.id,
                'default_state': 'draft'
            }
        }

    @api.constrains('student_id')
    def _check_student_id(self):
        for student in self:
            if self.search_count([('student_id', '=', student.student_id), ('id', '!=', student.id)]) > 0:
                raise ValidationError("Student ID must be unique!")

    @api.model
    def create(self, vals):
        """When creating a user with is_student=True, add them to the student group."""
        if vals.get('is_student'):
            student_group = self.env.ref('lms_module.group_lms_student', raise_if_not_found=False)
            if student_group:
                # Add the user to the student group
                # If there's an existing groups_id, we append (4, group_id)
                existing_groups = vals.get('groups_id', [])
                vals['groups_id'] = existing_groups + [(4, student_group.id)]
        return super().create(vals)