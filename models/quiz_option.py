from odoo import models, fields, api


class QuizOption(models.Model):
    _name = 'lms.quiz.option'
    _description = 'Quiz Question Option'
    _order = 'sequence, id'

    name = fields.Char(string='Option', required=True)
    question_id = fields.Many2one('lms.quiz.question', string='Question', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_correct = fields.Boolean(string='Is Correct', default=False)
    explanation = fields.Text(string='Explanation')
    active = fields.Boolean(default=True, tracking=True)

    # Statistics
    attempt_count = fields.Integer(string='Attempt Count', compute='_compute_statistics', store=True)
    selection_count = fields.Integer(string='Selection Count', compute='_compute_statistics', store=True)
    correct_count = fields.Integer(string='Correct Count', compute='_compute_statistics', store=True)

    @api.depends('attempt_ids')
    def _compute_statistics(self):
        for record in self:
            record.attempt_count = len(record.attempt_ids)
            record.selection_count = len(record.attempt_ids.filtered(lambda x: x.selected))
            record.correct_count = len(record.attempt_ids.filtered(lambda x: x.is_correct)) 