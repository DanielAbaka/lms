from odoo import models, fields, api
from odoo.exceptions import ValidationError

class QuizAttempt(models.Model):
    _name = 'lms.quiz.attempt'
    _description = 'Quiz Attempt'
    _order = 'start_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    quiz_id = fields.Many2one('lms.quiz', string='Quiz', required=True, ondelete='cascade')
    student_id = fields.Many2one('res.users', string='Student', required=True,
                                 domain=[('is_student','=',True)])
    enrollment_id = fields.Many2one('lms.enrollment', string='Enrollment', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', related='enrollment_id.course_id', store=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', related='enrollment_id.academic_year_id', store=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', related='enrollment_id.semester_id', store=True)
    start_date = fields.Datetime(string='Start Date', required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date')
    duration = fields.Integer(string='Duration (minutes)', compute='_compute_duration', store=True)
    score = fields.Float(string='Score', compute='_compute_score', store=True)
    max_score = fields.Float(string='Maximum Score', compute='_compute_score', store=True)
    percentage = fields.Float(string='Percentage', compute='_compute_score', store=True)
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='in_progress', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    question_attempt_ids = fields.One2many('lms.quiz.question.attempt', 'attempt_id', string='Question Attempts')
    grade_id = fields.Many2one('lms.grade', string='Grade')

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                duration_minutes = (record.end_date - record.start_date).total_seconds() / 60
                record.duration = round(duration_minutes)
            else:
                record.duration = 0

    @api.depends('question_attempt_ids')
    def _compute_score(self):
        for record in self:
            record.score = sum(record.question_attempt_ids.mapped('score'))
            record.max_score = sum(record.question_attempt_ids.mapped('max_score'))
            record.percentage = (record.score / record.max_score) * 100 if record.max_score else 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.quiz.attempt') or 'New'
        return super(QuizAttempt, self).create(vals)

    @api.constrains('student_id', 'enrollment_id')
    def _check_enrollment_student(self):
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError("Student must match the enrollment record!")

    @api.constrains('quiz_id', 'student_id')
    def _check_attempt_limit(self):
        for record in self:
            if record.quiz_id.max_attempts > 0:
                attempts = self.search_count([
                    ('quiz_id', '=', record.quiz_id.id),
                    ('student_id', '=', record.student_id.id),
                    ('id', '!=', record.id)
                ])
                if attempts >= record.quiz_id.max_attempts:
                    raise ValidationError("Maximum number of attempts reached for this quiz!")

    def action_submit(self):
        self.ensure_one()
        if self.state == 'in_progress':
            self.write({
                'state': 'completed',
                'end_date': fields.Datetime.now()
            })
            self._create_grade()

    def action_timeout(self):
        self.ensure_one()
        if self.state == 'in_progress':
            self.write({
                'state': 'timeout',
                'end_date': fields.Datetime.now()
            })
            self._create_grade()

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'in_progress':
            self.write({'state': 'cancelled'})

    def _create_grade(self):
        self.ensure_one()
        if self.state in ['completed', 'timeout']:
            grade_vals = {
                'student_id': self.student_id.id,
                'enrollment_id': self.enrollment_id.id,
                'quiz_id': self.quiz_id.id,
                'grade': self.percentage,
                'credits': self.quiz_id.total_points,
                'grade_type': 'quiz',
                'date': fields.Date.context_today(self),
                'grading_date': fields.Datetime.now(),
                'graded_by': self.env.user.id
            }
            self.grade_id = self.env['lms.grade'].create(grade_vals)