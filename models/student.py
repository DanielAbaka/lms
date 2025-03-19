from odoo import models, fields, api

class StudentProfile(models.Model):
    _inherit = 'res.users'

    is_student = fields.Boolean(string="Is Student", default=False)
    student_id = fields.Char(string="Student ID", required=True, unique=True)
    enrolled_courses = fields.Many2many('slide.channel', string="Enrolled Courses")
    dashboard_data = fields.Text(string="Dashboard Data", compute="_compute_dashboard_data")

    @api.depends('enrolled_courses')
    def _compute_dashboard_data(self):
        for record in self:
            enrolled_courses = record.enrolled_courses.mapped('name')
            record.dashboard_data = f"Enrolled Courses: {', '.join(enrolled_courses)}"