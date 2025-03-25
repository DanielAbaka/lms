from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Semester(models.Model):
    _name = 'lms.semester'
    _description = 'Academic Semester'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'academic_year_id desc, sequence'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', required=True, default=1)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    enrollment_start = fields.Date(string='Enrollment Start', tracking=True)
    enrollment_end = fields.Date(string='Enrollment End', tracking=True)
    add_drop_start = fields.Date(string='Add/Drop Start', tracking=True)
    add_drop_end = fields.Date(string='Add/Drop End', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    
    # Related Records
    enrollment_ids = fields.One2many('lms.enrollment', 'semester_id', string='Enrollments')
    course_ids = fields.One2many('slide.channel', 'semester_id', string='Courses')
    teacher_assignment_ids = fields.One2many('lms.teacher.assignment', 'semester_id', string='Teacher Assignments')
    quiz_ids = fields.One2many('lms.quiz', 'semester_id', string='Quizzes')
    grade_ids = fields.One2many('lms.grade', 'semester_id', string='Grades')
    document_ids = fields.One2many('lms.document', 'semester_id', string='Documents')

    # Statistics
    student_count = fields.Integer(string='Student Count', compute='_compute_statistics', store=True)
    course_count = fields.Integer(string='Course Count', compute='_compute_statistics', store=True)
    teacher_count = fields.Integer(string='Teacher Count', compute='_compute_statistics', store=True)
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_statistics', store=True)

    @api.depends('enrollment_ids', 'course_ids', 'teacher_assignment_ids')
    def _compute_statistics(self):
        for record in self:
            record.student_count = len(record.enrollment_ids.mapped('student_id'))
            record.course_count = len(record.course_ids)
            record.teacher_count = len(record.teacher_assignment_ids.mapped('teacher_id'))
            record.enrollment_count = len(record.enrollment_ids)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError("End date must be after start date!")

    @api.constrains('enrollment_start', 'enrollment_end')
    def _check_enrollment_dates(self):
        for record in self:
            if record.enrollment_start and record.enrollment_end:
                if record.enrollment_start >= record.enrollment_end:
                    raise ValidationError("Enrollment end date must be after enrollment start date!")

    @api.constrains('add_drop_start', 'add_drop_end')
    def _check_add_drop_dates(self):
        for record in self:
            if record.add_drop_start and record.add_drop_end:
                if record.add_drop_start >= record.add_drop_end:
                    raise ValidationError("Add/Drop end date must be after Add/Drop start date!")

    def action_activate(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'active'})

    def action_complete(self):
        self.ensure_one()
        if self.state == 'active':
            self.write({'state': 'completed'})

    def action_cancel(self):
        self.ensure_one()
        if self.state in ['draft', 'active']:
            self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.write({'state': 'draft'})

    @api.model
    def set_current_semester(self, semester_id):
        self.search([]).write({'is_current': False})
        semester = self.browse(semester_id)
        semester.is_current = True