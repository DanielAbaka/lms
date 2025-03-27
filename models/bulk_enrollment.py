from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BulkEnrollment(models.TransientModel):
    _name = 'lms.bulk.enrollment'
    _description = 'Bulk Student Enrollment'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True)
    course_ids = fields.Many2many('slide.channel', string='Courses', required=True)
    student_ids = fields.Many2many('res.users', string='Students', 
                                   domain=[('is_student', '=', True)],
                                   required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft', tracking=True)
    error_message = fields.Text(string='Error Message', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.bulk.enrollment') or 'New'
        return super(BulkEnrollment, self).create(vals)

    def action_process(self):
        self.ensure_one()
        self.write({'state': 'processing'})
        try:
            for student in self.student_ids:
                for course in self.course_ids:
                    enrollment_vals = {
                        'student_id': student.id,
                        'course_id': course.id,
                        'academic_year_id': self.academic_year_id.id,
                        'semester_id': self.semester_id.id,
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'admin_id': self.admin_id.id,
                        'state': 'draft'
                    }
                    self.env['lms.enrollment'].create(enrollment_vals)
            self.write({'state': 'completed'})
        except Exception as e:
            self.write({
                'state': 'failed',
                'error_message': str(e)
            })