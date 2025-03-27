from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AcademicYear(models.Model):
    _name = 'lms.academic.year'
    _description = 'Academic Year'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # Related Records
    semester_ids = fields.One2many('lms.semester', 'academic_year_id', string='Semesters')
    enrollment_ids = fields.One2many('lms.enrollment', 'academic_year_id', string='Enrollments')
    course_ids = fields.One2many('slide.channel', 'academic_year_id', string='Courses')
    teacher_assignment_ids = fields.One2many('lms.teacher.assignment', 'academic_year_id', string='Teacher Assignments')
    quiz_ids = fields.One2many('lms.quiz', 'academic_year_id', string='Quizzes')
    grade_ids = fields.One2many('lms.grade', 'academic_year_id', string='Grades')
    document_ids = fields.One2many('lms.document', 'academic_year_id', string='Documents')

    # Statistics
    student_count = fields.Integer(string='Student Count', compute='_compute_statistics', store=True)
    course_count = fields.Integer(string='Course Count', compute='_compute_statistics', store=True)
    teacher_count = fields.Integer(string='Teacher Count', compute='_compute_statistics', store=True)
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_statistics', store=True)
    semester_count = fields.Integer(string='Semester Count', compute='_compute_statistics', store=True)

    @api.depends('semester_ids', 'course_ids', 'enrollment_ids', 'teacher_assignment_ids')
    def _compute_statistics(self):
        for record in self:
            record.semester_count = len(record.semester_ids)
            record.student_count = len(record.enrollment_ids.mapped('student_id'))
            record.course_count = len(record.course_ids)
            record.teacher_count = len(record.teacher_assignment_ids.mapped('teacher_id'))
            record.enrollment_count = len(record.enrollment_ids)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError("End date must be after start date!")

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError("Academic year code must be unique!")

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
