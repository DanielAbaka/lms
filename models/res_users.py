from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    student_count = fields.Integer(compute='_compute_lms_stats', string='Total Students')
    course_count = fields.Integer(compute='_compute_lms_stats', string='Active Courses')
    teacher_count = fields.Integer(compute='_compute_lms_stats', string='Total Teachers')

    @api.depends('company_id')
    def _compute_lms_stats(self):
        for user in self:
            # Get counts from respective models
            user.student_count = self.env['res.users'].search_count([('is_student', '=', True)])
            user.course_count = self.env['slide.channel'].search_count([('state', '=', 'published')])
            user.teacher_count = self.env['res.users'].search_count([('is_teacher', '=', True)])

    def action_view_students(self):
        return {
            'name': 'Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('is_student', '=', True)],
            'context': {'default_is_student': True},
        }

    def action_view_courses(self):
        return {
            'name': 'Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'published')],
        }

    def action_view_teachers(self):
        return {
            'name': 'Teachers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('is_teacher', '=', True)],
            'context': {'default_is_teacher': True},
        } 