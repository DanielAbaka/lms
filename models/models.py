# -*- coding: utf-8 -*-

from odoo import models, fields, api


class lms_module(models.Model):
    _name = 'lms_module.lms_module'
    _description = 'lms_module.lms_module'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100



# class LMSQuiz(models.Model):
#     _inherit = 'survey.survey'

#     course_id = fields.Many2one('slide.channel', string="Related Course")

