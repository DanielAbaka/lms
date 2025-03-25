from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class Student(models.Model):
    _name = 'lms.student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Student'
    _order = 'registration_number'

    name = fields.Char(string='Name', required=True, tracking=True)
    registration_number = fields.Char(string='Registration Number', required=True, readonly=True,
                                    default=lambda self: self.env['ir.sequence'].next_by_code('lms.student'),
                                    tracking=True)
    active = fields.Boolean(default=True)
    image = fields.Binary(string='Photo')

    # Personal Information
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], required=True, tracking=True)
    blood_group = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('o+', 'O+'), ('o-', 'O-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
    ], string='Blood Group')

    # Contact Information
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    address = fields.Text(string='Address')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    zip_code = fields.Char(string='ZIP')

    # Academic Information
    current_semester_id = fields.Many2one('lms.semester', string='Current Semester', tracking=True)
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today, tracking=True)
    expected_graduation_date = fields.Date(string='Expected Graduation Date')
    previous_institution = fields.Char(string='Previous Institution')
    previous_qualification = fields.Char(string='Previous Qualification')
    
    # Related User
    user_id = fields.Many2one('res.users', string='Related User', ondelete='restrict')
    
    # Academic Records
    enrollment_ids = fields.One2many('lms.enrollment', 'student_id', string='Enrollments')
    attendance_ids = fields.One2many('lms.attendance', 'student_id', string='Attendance Records')
    assignment_submission_ids = fields.One2many('lms.assignment.submission', 'student_id', 
                                              string='Assignment Submissions')
    
    # Financial Records
    payment_ids = fields.One2many('lms.payment', 'student_id', string='Payments')
    total_fees = fields.Float(string='Total Fees', compute='_compute_fees', store=True)
    paid_amount = fields.Float(string='Paid Amount', compute='_compute_fees', store=True)
    balance_amount = fields.Float(string='Balance', compute='_compute_fees', store=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('enrolled', 'Enrolled'),
        ('alumni', 'Alumni'),
        ('terminated', 'Terminated')
    ], default='draft', string='Status', tracking=True)

    _sql_constraints = [
        ('unique_registration', 'unique(registration_number)', 'Registration number must be unique!'),
        ('unique_email', 'unique(email)', 'Email address must be unique!')
    ]

    @api.depends('payment_ids', 'enrollment_ids', 'enrollment_ids.course_id.fee')
    def _compute_fees(self):
        for student in self:
            total_fees = sum(student.enrollment_ids.mapped('course_id.fee'))
            paid_amount = sum(student.payment_ids.filtered(lambda p: p.state == 'posted').mapped('amount'))
            student.total_fees = total_fees
            student.paid_amount = paid_amount
            student.balance_amount = total_fees - paid_amount

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for record in self:
            if record.date_of_birth and record.date_of_birth > fields.Date.today():
                raise ValidationError('Date of birth cannot be in the future.')

    def action_enroll(self):
        self.write({'state': 'enrolled'})

    def action_terminate(self):
        self.write({'state': 'terminated'})

    def action_graduate(self):
        self.write({'state': 'alumni'})

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': 'Student Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Student Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'Student Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    @api.model
    def create(self, vals):
        # Create portal user for student
        if not vals.get('user_id') and vals.get('email'):
            user_vals = {
                'name': vals['name'],
                'login': vals['email'],
                'email': vals['email'],
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
            }
            user = self.env['res.users'].create(user_vals)
            vals['user_id'] = user.id

        return super(Student, self).create(vals)

    def write(self, vals):
        # Update related user information
        if 'email' in vals or 'name' in vals:
            for record in self:
                if record.user_id:
                    user_vals = {}
                    if 'email' in vals:
                        user_vals.update({
                            'login': vals['email'],
                            'email': vals['email']
                        })
                    if 'name' in vals:
                        user_vals['name'] = vals['name']
                    record.user_id.write(user_vals)

        return super(Student, self).write(vals)

    def unlink(self):
        # Prevent deletion of enrolled students
        for student in self:
            if student.state == 'enrolled':
                raise ValidationError('Cannot delete enrolled students.')
            if student.user_id:
                student.user_id.unlink()
        return super(Student, self).unlink()