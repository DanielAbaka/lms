from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Quiz(models.Model):
    _name = 'lms.quiz'
    _description = 'Course Quiz'
    _order = 'start_date desc, name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Quiz Code', required=True, copy=False)
    teacher_assignment_id = fields.Many2one(
        'lms.teacher.assignment', 
        string='Teacher Assignment', 
        required=True, 
        ondelete='cascade'
    )
    course_id = fields.Many2one(
        'slide.channel', 
        string='Course', 
        related='teacher_assignment_id.course_id', 
        store=True
    )
    academic_year_id = fields.Many2one(
        'lms.academic.year', 
        string='Academic Year', 
        related='teacher_assignment_id.academic_year_id', 
        store=True
    )
    semester_id = fields.Many2one(
        'lms.semester', 
        string='Semester', 
        related='teacher_assignment_id.semester_id', 
        store=True
    )
    description = fields.Text(string='Description')
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    duration = fields.Integer(string='Duration (minutes)', required=True)
    total_points = fields.Integer(string='Total Points', required=True)
    passing_score = fields.Integer(string='Passing Score', required=True)
    max_attempts = fields.Integer(string='Maximum Attempts', default=1)
    show_results = fields.Boolean(string='Show Results', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    active = fields.Boolean(default=True)

    # ADD: One2many field to link quiz questions
    question_ids = fields.One2many(
        'lms.quiz.question', 
        'quiz_id', 
        string='Questions'
    )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError("End date must be after start date!")

    @api.constrains('total_points', 'passing_score')
    def _check_scores(self):
        for record in self:
            if record.passing_score > record.total_points:
                raise ValidationError("Passing score cannot be greater than total points!")

    @api.constrains('max_attempts')
    def _check_attempts(self):
        for record in self:
            if record.max_attempts < 1:
                raise ValidationError("Maximum attempts must be at least 1!")

    def action_publish(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'published'})

    def action_start(self):
        self.ensure_one()
        if self.state == 'published':
            self.write({'state': 'in_progress'})

    def action_complete(self):
        self.ensure_one()
        if self.state == 'in_progress':
            self.write({'state': 'completed'})

    def action_cancel(self):
        self.ensure_one()
        if self.state in ['draft', 'published']:
            self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.write({'state': 'draft'})
