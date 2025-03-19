from odoo import models, fields, api

class Semester(models.Model):
    _name = 'lms.semester'
    _description = 'Semester'

    name = fields.Char(string="Semester Name", required=True)
    academic_year_id = fields.Many2one('lms.academic.year', string="Academic Year")
    is_current = fields.Boolean(string="Is Current Semester", default=False)

    @api.model
    def set_current_semester(self, semester_id):
        self.search([]).write({'is_current': False})
        semester = self.browse(semester_id)
        semester.is_current = True