from odoo import models, fields, api


class QuizQuestionAttempt(models.Model):
    _name = 'lms.quiz.question.attempt'
    _description = 'Quiz Question Attempt'
    _order = 'sequence, id'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    attempt_id = fields.Many2one('lms.quiz.attempt', string='Quiz Attempt', required=True)
    question_id = fields.Many2one('lms.quiz.question', string='Question', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    max_score = fields.Integer(string='Maximum Score', related='question_id.points', store=True)
    score = fields.Float(string='Score', compute='_compute_score', store=True)
    is_correct = fields.Boolean(string='Is Correct', compute='_compute_score', store=True)
    answer_text = fields.Text(string='Answer Text')
    selected_option_ids = fields.Many2many('lms.quiz.option', 'question_attempt_option_rel', 'attempt_id', 'option_id', string='Selected Options')
    time_spent = fields.Integer(string='Time Spent (seconds)')
    feedback = fields.Text(string='Feedback')
    active = fields.Boolean(default=True, tracking=True)

    @api.depends('question_id', 'answer_text', 'selected_option_ids')
    def _compute_score(self):
        for record in self:
            if record.question_id.question_type == 'multiple_choice':
                correct_options = record.question_id.correct_option_ids
                if record.selected_option_ids == correct_options:
                    record.score = record.max_score
                    record.is_correct = True
                else:
                    record.score = 0
                    record.is_correct = False
            elif record.question_id.question_type == 'true_false':
                correct_option = record.question_id.correct_option_ids[0]
                if record.selected_option_ids == correct_option:
                    record.score = record.max_score
                    record.is_correct = True
                else:
                    record.score = 0
                    record.is_correct = False
            elif record.question_id.question_type == 'short_answer':
                if record.answer_text and record.question_id.correct_answer:
                    # Simple keyword matching for short answers
                    keywords = record.question_id.keywords.split(',')
                    answer = record.answer_text.lower()
                    if any(keyword.strip().lower() in answer for keyword in keywords):
                        record.score = record.max_score
                        record.is_correct = True
                    else:
                        record.score = 0
                        record.is_correct = False
                else:
                    record.score = 0
                    record.is_correct = False
            else:  # essay
                record.score = 0
                record.is_correct = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.quiz.question.attempt') or 'New'
        return super(QuizQuestionAttempt, self).create(vals) 