from odoo import models, fields, api

class TeacherProfile(models.Model):
    _inherit = 'res.users'

    # Make default=False so that only the Teacher form sets them to True
    is_teacher = fields.Boolean(string="Is Teacher", default=False)

    assigned_courses = fields.Many2many(
        'slide.channel',
        'lms_teacher_course_rel',
        'teacher_id',
        'course_id',
        string="Assigned Courses"
    )

    @api.model
    def create(self, vals):
        """When creating a user with is_teacher=True, add them to the teacher group."""
        if vals.get('is_teacher'):
            teacher_group = self.env.ref('lms_module.group_lms_teacher', raise_if_not_found=False)
            if teacher_group:
                # Add the user to the teacher group
                # If there's an existing groups_id, we append (4, group_id)
                existing_groups = vals.get('groups_id', [])
                vals['groups_id'] = existing_groups + [(4, teacher_group.id)]
        return super().create(vals)