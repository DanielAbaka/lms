from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class LMSCourse(models.Model):
    _inherit = 'slide.channel'  # Inherits from the eLearning module
    _description = 'LMS Course'

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

    # New fields for enhanced views
    code = fields.Char(string="Course Code", required=True, copy=False)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    max_students = fields.Integer(string="Maximum Students", default=30)
    objectives = fields.Text(string="Course Objectives")
    prerequisites = fields.Text(string="Course Prerequisites")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published')
    ], string='Status', default='draft', required=True)
    enrollment_count = fields.Integer(compute='_compute_enrollment_count', string='Enrollment Count')
    assignment_count = fields.Integer(compute='_compute_assignment_count', string='Assignment Count')

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for course in self:
            course.enrollment_count = len(course.enrollment_ids)

    @api.depends('teacher_assignment_ids')
    def _compute_assignment_count(self):
        for course in self:
            course.assignment_count = len(course.teacher_assignment_ids)

    def action_publish(self):
        self.write({'state': 'published'})

    def action_unpublish(self):
        self.write({'state': 'draft'})

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': 'Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
        }

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'name': 'Teacher Assignments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.teacher.assignment',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    @api.constrains('max_students')
    def _check_max_students(self):
        for course in self:
            if course.max_students < 1:
                raise ValidationError("Maximum students must be at least 1.")