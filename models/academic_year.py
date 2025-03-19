from odoo import models, fields

class AcademicYear(models.Model):
    _name = 'lms.academic.year'
    _description = 'Academic Year'

    name = fields.Char(string="Academic Year", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    semester_ids = fields.One2many('lms.semester', 'academic_year_id', string="Semesters")