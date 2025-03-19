from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LMSCoursePlanning(models.Model):
    _name = 'lms.course.planning'
    _description = 'Student Course Planning'

    student_id = fields.Many2one('res.users', string="Student", required=True, domain=[('is_student', '=', True)])
    semester_id = fields.Many2one('lms.semester', string="Semester", required=True)
    course_ids = fields.Many2many('slide.channel', string="Planned Courses")
    total_credits = fields.Integer(string="Total Credits", compute="_compute_total_credits", store=True)
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)
    enrollment_id = fields.Many2one('lms.enrollment', string="Enrollment")
    is_enrolled = fields.Boolean(string="Enrolled", compute="_compute_is_enrolled", store=True)

    @api.depends('course_ids')
    def _compute_total_credits(self):
        for record in self:
            record.total_credits = sum(record.course_ids.mapped('credits'))

    @api.depends('course_ids')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = sum(course.credits * course.cost_per_credit for course in record.course_ids)

    @api.depends('enrollment_id')
    def _compute_is_enrolled(self):
        for record in self:
            record.is_enrolled = bool(record.enrollment_id)

    def enroll_student(self):
        enrollment = self.env['lms.enrollment'].create({
            'student_id': self.student_id.id,
            'course_id': [(6, 0, self.course_ids.ids)],
            'enrollment_date': fields.Date.today(),
            'payment_status': 'pending',
            'total_cost': self.total_cost,
        })
        self.enrollment_id = enrollment.id