from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LMSGrade(models.Model):
    _name = 'lms.grade'
    _description = 'LMS Student Grades'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, student_id'

    name = fields.Char(string='Grade Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    student_id = fields.Many2one('lms.student', string='Student', required=True)
    enrollment_id = fields.Many2one('lms.enrollment', string='Enrollment', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True)
    quiz_id = fields.Many2one('lms.quiz', string='Quiz')
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', related='enrollment_id.academic_year_id', store=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', related='enrollment_id.semester_id', store=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    grade = fields.Float(string='Final Grade', required=True)
    credits = fields.Integer(string='Credits', required=True)
    grade_type = fields.Selection([
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('exam', 'Examination'),
        ('project', 'Project'),
        ('participation', 'Participation')
    ], string='Grade Type', required=True)
    remarks = fields.Text(string='Teacher Comments')
    is_final = fields.Boolean(string='Is Final Grade', default=False)
    graded_by = fields.Many2one('res.users', string='Graded By', readonly=True, default=lambda self: self.env.user)
    grading_date = fields.Datetime(string='Grading Date', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lms.grade') or 'New'
        return super(LMSGrade, self).create(vals)

    def action_submit_grade(self):
        self.ensure_one()
        if not self.grading_date:
            self.write({
                'grading_date': fields.Datetime.now(),
                'graded_by': self.env.user.id
            })

    def action_reset_grade(self):
        self.ensure_one()
        if self.grading_date:
            self.write({
                'grading_date': False,
                'graded_by': False
            })

    @api.constrains('grade')
    def _check_grade(self):
        for record in self:
            if record.grade < 0 or record.grade > 100:
                raise ValidationError("Grade must be between 0 and 100!")

    @api.constrains('credits')
    def _check_credits(self):
        for record in self:
            if record.credits <= 0:
                raise ValidationError("Credits must be greater than 0!")

    @api.constrains('enrollment_id', 'student_id')
    def _check_enrollment_student(self):
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError("Student must match the enrollment record!")