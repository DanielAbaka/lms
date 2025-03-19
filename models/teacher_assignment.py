from odoo import models, fields

class LMSTeacherAssignment(models.Model):
    _name = 'lms.teacher.assignment'
    _description = 'Teacher Assignment'
    _auto = True  # ✅ Ensures Odoo creates the database table

    teacher_id = fields.Many2one(
        'res.users', 
        string="Teacher", 
        required=True,
        domain=[('is_teacher', '=', True)]  # ✅ Restrict to teachers only
    )
    course_id = fields.Many2one('slide.channel', string="Course", required=True)
    start_date = fields.Date(string="Start Date", default=fields.Date.today)
    end_date = fields.Date(string="End Date")