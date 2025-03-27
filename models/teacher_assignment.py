from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TeacherAssignment(models.Model):
    _name = 'lms.teacher.assignment'
    _description = 'Teacher Course Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'academic_year_id desc, semester_id desc, teacher_id'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    teacher_id = fields.Many2one('res.users', string='Teacher', required=True, domain=[('is_teacher', '=', True)])
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    course_id = fields.Many2one('slide.channel', string='Course', required=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    schedule = fields.Text(string='Schedule')
    classroom = fields.Char(string='Classroom')
    max_students = fields.Integer(string='Maximum Students')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # Related Records
    schedule_template_id = fields.Many2one('lms.schedule.template', string='Schedule Template')
    bulk_wizard_id = fields.Many2one('lms.schedule.bulk.wizard', string='Bulk Wizard')
    enrollment_ids = fields.One2many('lms.enrollment', 'teacher_assignment_id', string='Enrollments')
    attendance_ids = fields.One2many('lms.attendance', 'teacher_assignment_id', string='Attendance')
    grade_ids = fields.One2many('lms.grade', 'teacher_assignment_id', string='Grades')
    quiz_ids = fields.One2many('lms.quiz', 'teacher_assignment_id', string='Quizzes')
    document_ids = fields.One2many('lms.document', 'teacher_assignment_id', string='Documents')
    schedule_ids = fields.One2many('lms.schedule', 'teacher_assignment_id', string='Schedules')

    # Statistics
    student_count = fields.Integer(string='Student Count', compute='_compute_statistics', store=True)
    attendance_rate = fields.Float(string='Attendance Rate', compute='_compute_statistics', store=True)
    average_grade = fields.Float(string='Average Grade', compute='_compute_statistics', store=True)

    @api.depends('enrollment_ids', 'attendance_ids', 'grade_ids')
    def _compute_statistics(self):
        for record in self:
            record.student_count = len(record.enrollment_ids)
            
            # Calculate attendance rate
            total_sessions = len(record.attendance_ids)
            if total_sessions > 0:
                present_sessions = len(record.attendance_ids.filtered(lambda x: x.status == 'present'))
                record.attendance_rate = (present_sessions / total_sessions) * 100
            else:
                record.attendance_rate = 0.0

            # Calculate average grade
            grades = record.grade_ids.mapped('grade')
            if grades:
                record.average_grade = sum(grades) / len(grades)
            else:
                record.average_grade = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.teacher.assignment') or 'New'
        return super(TeacherAssignment, self).create(vals)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError("End date must be after start date!")

    @api.constrains('teacher_id', 'course_id', 'academic_year_id', 'semester_id')
    def _check_duplicate_assignment(self):
        for record in self:
            domain = [
                ('teacher_id', '=', record.teacher_id.id),
                ('course_id', '=', record.course_id.id),
                ('academic_year_id', '=', record.academic_year_id.id),
                ('semester_id', '=', record.semester_id.id),
                ('id', '!=', record.id)
            ]
            if self.search_count(domain) > 0:
                raise ValidationError("This teacher is already assigned to this course for the selected academic year and semester!")

    def action_assign(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'assigned'})

    def action_start(self):
        self.ensure_one()
        if self.state == 'assigned':
            self.write({'state': 'in_progress'})

    def action_complete(self):
        self.ensure_one()
        if self.state == 'in_progress':
            self.write({'state': 'completed'})

    def action_cancel(self):
        self.ensure_one()
        if self.state in ['draft', 'assigned']:
            self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.write({'state': 'draft'})