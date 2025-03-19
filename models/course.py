from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class LMSCourse(models.Model):
    _inherit = 'slide.channel'  # Inherits from the eLearning module

    academic_year_id = fields.Many2one('lms.academic.year', string="Academic Year")
    semester_id = fields.Many2one('lms.semester', string="Semester")
    prerequisite_course_ids = fields.Many2many(
        'slide.channel', 
        'lms_course_prerequisite_rel',  # Explicit table name
        'course_id', 
        'prerequisite_id', 
        string="Prerequisites"
    )
    credits = fields.Integer(string="Credits", default=3)
    teacher_assignment_ids = fields.One2many('lms.teacher.assignment', 'course_id', string="Assigned Teachers")