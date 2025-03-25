from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class LMSCourse(models.Model):
    _name = 'lms.course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'LMS Course'
    _order = 'sequence, id'

    # Basic Information
    name = fields.Char(string='Course Name', required=True, tracking=True)
    code = fields.Char(string='Course Code', required=True, readonly=True,
                      default=lambda self: self.env['ir.sequence'].next_by_code('lms.course'),
                      tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
    image = fields.Binary(string='Course Image')
    
    # Academic Details
    credits = fields.Integer(string='Credits', required=True, tracking=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True, tracking=True)
    department_id = fields.Many2one('lms.department', string='Department', tracking=True)
    level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='beginner', required=True, tracking=True)
    
    # Course Content
    description = fields.Html(string='Description')
    objectives = fields.Html(string='Course Objectives')
    syllabus = fields.Html(string='Syllabus')
    grading_criteria = fields.Html(string='Grading Criteria')
    prerequisites = fields.Many2many('lms.course', 
                                   'course_prerequisites_rel',
        'course_id', 
        'prerequisite_id', 
                                   string='Prerequisites')
    
    # Teaching Staff
    teacher_id = fields.Many2one('lms.teacher', string='Primary Teacher', tracking=True)
    assistant_teacher_ids = fields.Many2many('lms.teacher', 'course_assistant_teachers_rel',
                                           'course_id', 'teacher_id', 
                                           string='Assistant Teachers')
    
    # Schedule Information
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    schedule_ids = fields.One2many('lms.course.schedule', 'course_id', string='Schedule')
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    
    # Content Management
    material_ids = fields.One2many('lms.course.material', 'course_id', string='Course Materials')
    material_count = fields.Integer(compute='_compute_material_count', store=True)
    assignment_ids = fields.One2many('lms.assignment', 'course_id', string='Assignments')
    assignment_count = fields.Integer(compute='_compute_assignment_count', store=True)
    quiz_ids = fields.One2many('lms.quiz', 'course_id', string='Quizzes')
    quiz_count = fields.Integer(compute='_compute_quiz_count', store=True)
    
    # Enrollment Management
    enrollment_ids = fields.One2many('lms.enrollment', 'course_id', string='Enrollments')
    enrolled_student_count = fields.Integer(string='Enrolled Students', 
                                          compute='_compute_enrolled_students',
                                          store=True)
    max_students = fields.Integer(string='Maximum Students', tracking=True)
    min_students = fields.Integer(string='Minimum Students', default=1)
    enrollment_deadline = fields.Date(string='Enrollment Deadline')
    waiting_list_ids = fields.One2many('lms.waiting.list', 'course_id', string='Waiting List')
    waiting_list_count = fields.Integer(compute='_compute_waiting_list_count')
    
    # Attendance
    attendance_ids = fields.One2many('lms.attendance', 'course_id', string='Attendance Records')
    attendance_required = fields.Boolean(string='Attendance Required', default=True)
    minimum_attendance = fields.Float(string='Minimum Attendance %', default=75)
    
    # Financial
    fee = fields.Float(string='Course Fee', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    payment_schedule_ids = fields.One2many('lms.payment.schedule', 'course_id', 
                                         string='Payment Schedule')
    
    # Progress Tracking
    progress_tracking = fields.Selection([
        ('none', 'No Tracking'),
        ('materials', 'Materials Only'),
        ('assignments', 'Assignments Only'),
        ('both', 'Materials and Assignments')
    ], default='both', string='Progress Tracking')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', string='Status', tracking=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Course code must be unique!'),
    ]

    # Compute Methods
    @api.depends('enrollment_ids', 'enrollment_ids.state')
    def _compute_enrolled_students(self):
        for course in self:
            course.enrolled_student_count = len(course.enrollment_ids.filtered(
                lambda e: e.state == 'enrolled'))

    @api.depends('schedule_ids', 'schedule_ids.duration')
    def _compute_duration(self):
        for course in self:
            course.duration = sum(course.schedule_ids.mapped('duration'))

    @api.depends('material_ids')
    def _compute_material_count(self):
        for course in self:
            course.material_count = len(course.material_ids)

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        for course in self:
            course.assignment_count = len(course.assignment_ids)

    @api.depends('quiz_ids')
    def _compute_quiz_count(self):
        for course in self:
            course.quiz_count = len(course.quiz_ids)

    @api.depends('waiting_list_ids')
    def _compute_waiting_list_count(self):
        for course in self:
            course.waiting_list_count = len(course.waiting_list_ids)

    # Constraint Methods
    @api.constrains('max_students', 'min_students')
    def _check_student_limits(self):
        for record in self:
            if record.max_students and record.min_students:
                if record.max_students < record.min_students:
                    raise ValidationError('Maximum students cannot be less than minimum students.')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError('End date must be after start date.')

    @api.constrains('fee')
    def _check_fee(self):
        for record in self:
            if record.fee < 0:
                raise ValidationError('Course fee cannot be negative.')

    # Action Methods
    def action_submit_approval(self):
        for record in self:
            if not record.teacher_id:
                raise ValidationError('Please assign a teacher before submitting for approval.')
            if not record.schedule_ids:
                raise ValidationError('Please set up course schedule before submitting for approval.')
        self.write({'state': 'pending'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_start(self):
        for record in self:
            if record.enrolled_student_count < record.min_students:
                raise ValidationError('Minimum number of students not met.')
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_view_materials(self):
        self.ensure_one()
        return {
            'name': 'Course Materials',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.course.material',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': 'Enrolled Students',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id), ('state', '=', 'enrolled')],
            'context': {'default_course_id': self.id},
        }

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'name': 'Course Assignments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.assignment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'Course Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    def action_view_waiting_list(self):
        self.ensure_one()
        return {
            'name': 'Waiting List',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.waiting.list',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    # CRUD Methods
    @api.model
    def create(self, vals):
        # Set enrollment deadline if not provided
        if not vals.get('enrollment_deadline') and vals.get('start_date'):
            start_date = fields.Date.from_string(vals['start_date'])
            vals['enrollment_deadline'] = start_date - timedelta(days=7)
        
        # Validate prerequisites
        if vals.get('prerequisites'):
            self._validate_prerequisites(vals['prerequisites'][0][2])
            
        return super(LMSCourse, self).create(vals)

    def write(self, vals):
        # Validate state changes
        if vals.get('state') == 'in_progress':
            for record in self:
                if not record.teacher_id:
                    raise ValidationError('Cannot start course without assigned teacher.')
                if not record.schedule_ids:
                    raise ValidationError('Cannot start course without schedule.')
        
        # Validate prerequisites
        if vals.get('prerequisites'):
            self._validate_prerequisites(vals['prerequisites'][0][2])
            
        return super(LMSCourse, self).write(vals)

    def unlink(self):
        # Prevent deletion of courses with enrollments
        for record in self:
            if record.enrollment_ids:
                raise ValidationError('Cannot delete course with existing enrollments.')
        return super(LMSCourse, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'code': self.env['ir.sequence'].next_by_code('lms.course'),
            'enrollment_ids': [],
            'state': 'draft',
            'schedule_ids': [],
            'attendance_ids': [],
        })
        return super(LMSCourse, self).copy(default)

    # Helper Methods
    def _validate_prerequisites(self, prerequisite_ids):
        """Validate that prerequisites don't create circular dependencies"""
        if not prerequisite_ids:
            return
        
        courses_to_check = self.browse(prerequisite_ids)
        for course in courses_to_check:
            if self.id in course.prerequisites.ids:
                raise ValidationError(
                    f'Circular prerequisite dependency detected with course {course.name}'
                )

    def generate_course_completion_report(self):
        """Generate a detailed course completion report"""
        self.ensure_one()
        return self.env.ref('lms.action_report_course_completion')\
                   .report_action(self)

    def notify_enrolled_students(self, message):
        """Send notification to all enrolled students"""
        for record in self:
            students = record.enrollment_ids.mapped('student_id')
            for student in students:
                self.env['mail.message'].create({
                    'body': message,
                    'subject': f'Course Update: {record.name}',
                    'partner_ids': [(4, student.user_id.partner_id.id)],
                    'model': 'lms.course',
                    'res_id': record.id,
                })

    def check_prerequisites_met(self, student_id):
        """Check if a student meets all prerequisites"""
        self.ensure_one()
        student = self.env['lms.student'].browse(student_id)
        completed_courses = student.enrollment_ids.filtered(
            lambda e: e.state == 'completed'
        ).mapped('course_id')
        
        for prerequisite in self.prerequisites:
            if prerequisite not in completed_courses:
                return False
        return True

    