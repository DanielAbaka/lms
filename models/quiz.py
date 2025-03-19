from odoo import models, fields, api

class LMSQuiz(models.Model):
    _inherit = 'survey.survey'

    course_id = fields.Many2one('slide.channel', string="Related Course")