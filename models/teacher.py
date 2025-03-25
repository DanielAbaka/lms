from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class Teacher(models.Model):
    _inherit = 'res.users'
    _description = 'Teacher'

    # Existing fields
    is_teacher = fields.Boolean(string='Is Teacher', default=True)
    teacher_id = fields.Char(string='Teacher ID', required=True, copy=False)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    specialization = fields.Char(string='Specialization')
    qualification = fields.Char(string='Qualification')
    joining_date = fields.Date(string='Joining Date')
    department = fields.Char(string='Department')
    office_location = fields.Char(string='Office Location')
    office_hours = fields.Text(string='Office Hours')

    # New fields for teacher portal
    assigned_course_ids = fields.One2many('lms.teacher.assignment', 'teacher_id', string='Assigned Courses')
    course_material_ids = fields.One2many('lms.course.material', 'teacher_ids', string='Course Materials')
    attendance_ids = fields.One2many('lms.attendance', 'marked_by', string='Attendance Records')
    quiz_ids = fields.One2many('lms.quiz', 'teacher_assignment_id', string='Quizzes', domain=[('teacher_assignment_id.teacher_id', '=', lambda self: self.id)])
    
    # Computed fields for dashboard
    current_course_count = fields.Integer(compute='_compute_teacher_stats', string='Current Courses')
    total_student_count = fields.Integer(compute='_compute_teacher_stats', string='Total Students')
    average_attendance_rate = fields.Float(compute='_compute_teacher_stats', string='Average Attendance')
    pending_gradings = fields.Integer(compute='_compute_teacher_stats', string='Pending Gradings')

    @api.depends('assigned_course_ids', 'attendance_ids', 'quiz_ids')
    def _compute_teacher_stats(self):
        for teacher in self:
            # Count current courses
            teacher.current_course_count = len(teacher.assigned_course_ids.filtered(
                lambda a: a.state == 'active' and a.end_date >= fields.Date.today()
            ))

            # Count total students
            teacher.total_student_count = len(teacher.assigned_course_ids.mapped('course_id').mapped('enrollment_ids').mapped('student_id'))

            # Calculate average attendance rate
            attendances = teacher.attendance_ids.filtered(lambda a: a.date >= fields.Date.today() - timedelta(days=30))
            if attendances:
                present_count = len(attendances.filtered(lambda a: a.status == 'present'))
                teacher.average_attendance_rate = (present_count / len(attendances)) * 100
            else:
                teacher.average_attendance_rate = 0.0

            # Count pending gradings
            teacher.pending_gradings = len(teacher.quiz_ids.filtered(lambda q: q.state == 'submitted'))

    def action_view_courses(self):
        self.ensure_one()
        return {
            'name': 'My Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.teacher.assignment',
            'view_mode': 'tree,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id},
        }

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': 'My Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('is_student', '=', True), 
                      ('enrollment_ids.course_id', 'in', self.assigned_course_ids.mapped('course_id').ids)],
        }

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'Attendance Records',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('marked_by', '=', self.id)],
            'context': {'default_marked_by': self.id},
        }

    def action_view_materials(self):
        self.ensure_one()
        return {
            'name': 'Course Materials',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.course.material',
            'view_mode': 'tree,form',
            'domain': [('teacher_ids', 'in', [self.id])],
            'context': {'default_teacher_ids': [(4, self.id)]},
        }

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'name': 'Assignments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.assignment',
            'view_mode': 'tree,form',
            'domain': [('teacher_assignment_id.teacher_id', '=', self.id)],
            'context': {'default_teacher_assignment_id': False},
        }

    def action_view_quizzes(self):
        self.ensure_one()
        return {
            'name': 'Quizzes',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.quiz',
            'view_mode': 'tree,form',
            'domain': [('teacher_assignment_id.teacher_id', '=', self.id)],
            'context': {'default_teacher_assignment_id': False},
        }

    def action_take_attendance(self):
        self.ensure_one()
        return {
            'name': 'Take Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_marked_by': self.id,
                'default_date': fields.Date.today(),
                'default_session_type': 'lecture'
            }
        }

    def action_create_material(self):
        self.ensure_one()
        return {
            'name': 'Create Course Material',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.course.material',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_teacher_ids': [(4, self.id)],
                'default_is_published': False
            }
        }

    def action_create_assignment(self):
        self.ensure_one()
        return {
            'name': 'Create Assignment',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.assignment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_teacher_id': self.id,
                'default_state': 'draft'
            }
        }

    def action_create_quiz(self):
        self.ensure_one()
        return {
            'name': 'Create Quiz',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.quiz',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_teacher_assignment_id': False,
                'default_state': 'draft'
            }
        }

    def action_export_attendance(self):
        self.ensure_one()
        return {
            'name': 'Export Attendance',
            'type': 'ir.actions.act_url',
            'url': '/web/export/attendance/%s' % self.id,
            'target': 'self',
        }

    def action_view_analytics(self):
        self.ensure_one()
        return {
            'name': 'Performance Analytics',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.teacher.analytics',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_teacher_id': self.id},
        }

    @api.constrains('teacher_id')
    def _check_teacher_id(self):
        for teacher in self:
            if self.search_count([('teacher_id', '=', teacher.teacher_id), ('id', '!=', teacher.id)]) > 0:
                raise ValidationError("Teacher ID must be unique!")

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