from odoo import models, fields

class LMSGrade(models.Model):
    _name = 'lms.grade'
    _description = 'LMS Student Grades'

    student_id = fields.Many2one(
        'res.users',
        string="Student",
        required=True,
        domain=[('is_student', '=', True)]  # ✅ Only show student users
    )
    course_id = fields.Many2one('slide.channel', string="Course", required=True)
    grade = fields.Float(string="Final Grade", required=True)
    remarks = fields.Text(string="Teacher Comments")