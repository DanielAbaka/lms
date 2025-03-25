from odoo import models, fields, api
from datetime import date

class AcademicSemester(models.Model):
    _name = 'lms.semester'
    _description = 'Academic Semester'
    _order = 'start_date desc'

    name = fields.Char(string='Semester Name', required=True)
    academic_year = fields.Char(string='Academic Year', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', string='Status', tracking=True)
    
    course_ids = fields.One2many('lms.course', 'semester_id', string='Courses')
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("End date must be after start date")

    @api.model
    def set_current_semester(self, semester_id):
        self.search([]).write({'is_current': False})
        semester = self.browse(semester_id)
        semester.is_current = True