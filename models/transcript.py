from odoo import models, fields, api

class LMSTranscript(models.Model):
    _name = 'lms.transcript'
    _description = 'Student Transcript'

    student_id = fields.Many2one(
        'res.users',
        string="Student",
        required=True,
        domain=[('is_student', '=', True)]
    )
    academic_year_id = fields.Many2one('lms.academic.year', string="Academic Year")
    semester_id = fields.Many2one('lms.semester', string="Semester")
    course_ids = fields.Many2many('slide.channel', string="Courses Taken")
    total_credits = fields.Integer(string="Total Credits", compute="_compute_total_credits")
    gpa = fields.Float(string="GPA", compute="_compute_gpa")

    @api.depends('course_ids')
    def _compute_total_credits(self):
        for record in self:
            record.total_credits = sum(course.credits for course in record.course_ids)

    @api.depends('student_id')
    def _compute_gpa(self):
        for record in self:
            grades = self.env['lms.grade'].search([('student_id', '=', record.student_id.id)])
            if grades:
                total_weighted_score = sum(
                    grade.grade * grade.course_id.credits
                    for grade in grades
                )
                total_credits = sum(
                    grade.course_id.credits
                    for grade in grades if grade.course_id.credits > 0
                )
                record.gpa = total_weighted_score / total_credits if total_credits else 0.0
            else:
                record.gpa = 0.0