from odoo import models, fields, api
from odoo.exceptions import ValidationError


class QuizQuestion(models.Model):
    _name = 'lms.quiz.question'
    _description = 'Quiz Question'
    _order = 'sequence, id'

    name = fields.Char(string='Question', required=True)
    quiz_id = fields.Many2one('lms.quiz', string='Quiz', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    question_type = fields.Selection([
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay')
    ], string='Question Type', required=True)
    points = fields.Integer(string='Points', required=True, default=1)
    explanation = fields.Text(string='Explanation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # Question Options
    option_ids = fields.One2many('lms.quiz.option', 'question_id', string='Options')
    correct_option_ids = fields.Many2many('lms.quiz.option', 'question_correct_option_rel', 'question_id', 'option_id', string='Correct Options')
    correct_answer = fields.Text(string='Correct Answer')
    keywords = fields.Text(string='Keywords (for Short Answer)')

    # Statistics
    attempt_count = fields.Integer(string='Attempt Count', compute='_compute_statistics', store=True)
    correct_count = fields.Integer(string='Correct Count', compute='_compute_statistics', store=True)
    average_score = fields.Float(string='Average Score', compute='_compute_statistics', store=True)

    @api.depends('option_ids.attempt_ids')
    def _compute_statistics(self):
        for record in self:
            attempts = record.option_ids.mapped('attempt_ids')
            record.attempt_count = len(attempts)
            correct_attempts = attempts.filtered(lambda x: x.is_correct)
            record.correct_count = len(correct_attempts)
            if record.attempt_count > 0:
                record.average_score = (record.correct_count / record.attempt_count) * 100
            else:
                record.average_score = 0.0

    @api.constrains('question_type', 'option_ids')
    def _check_options(self):
        for record in self:
            if record.question_type in ['multiple_choice', 'true_false']:
                if not record.option_ids:
                    raise ValidationError("Multiple choice and true/false questions must have options!")
                if record.question_type == 'true_false' and len(record.option_ids) != 2:
                    raise ValidationError("True/False questions must have exactly 2 options!")

    @api.constrains('question_type', 'correct_option_ids')
    def _check_correct_options(self):
        for record in self:
            if record.question_type in ['multiple_choice', 'true_false']:
                if not record.correct_option_ids:
                    raise ValidationError("Please select at least one correct option!")

    @api.constrains('question_type', 'correct_answer')
    def _check_correct_answer(self):
        for record in self:
            if record.question_type == 'short_answer' and not record.correct_answer:
                raise ValidationError("Short answer questions must have a correct answer!")

    @api.constrains('points')
    def _check_points(self):
        for record in self:
            if record.points <= 0:
                raise ValidationError("Points must be greater than 0!")

    def action_activate(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'active'})

    def action_archive(self):
        self.ensure_one()
        if self.state == 'active':
            self.write({'state': 'archived'})

    def action_unarchive(self):
        self.ensure_one()
        if self.state == 'archived':
            self.write({'state': 'active'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state in ['active', 'archived']:
            self.write({'state': 'draft'}) 