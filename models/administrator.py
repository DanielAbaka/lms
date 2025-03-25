from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Administrator(models.Model):
    _inherit = 'res.users'
    _description = 'Administrator'

    # Existing fields
    is_admin = fields.Boolean(string='Is Administrator', default=True)
    administrator_code = fields.Char(string='Administrator Code', required=True, copy=False)
    department = fields.Char(string='Department')
    position = fields.Char(string='Position')
    joining_date = fields.Date(string='Joining Date')
    office_location = fields.Char(string='Office Location')
    office_hours = fields.Text(string='Office Hours')

    # Computed fields for related records
    academic_year_ids = fields.One2many('lms.academic.year', 'admin_id', string='Academic Years', compute='_compute_related_records')
    semester_ids = fields.One2many('lms.semester', 'admin_id', string='Semesters', compute='_compute_related_records')
    student_ids = fields.One2many('lms.student', 'admin_id', string='Students', compute='_compute_related_records')
    teacher_ids = fields.One2many('lms.teacher', 'admin_id', string='Teachers', compute='_compute_related_records')
    revenue_ids = fields.One2many('lms.payment', 'admin_id', string='Revenue', compute='_compute_related_records', domain=[('state', '=', 'paid')])
    pending_payment_ids = fields.One2many('lms.payment', 'admin_id', string='Pending Payments', compute='_compute_related_records', domain=[('state', '=', 'pending')])
    
    # Computed fields for dashboard
    total_student_count = fields.Integer(compute='_compute_admin_stats', string='Total Students')
    total_teacher_count = fields.Integer(compute='_compute_admin_stats', string='Total Teachers')
    total_course_count = fields.Integer(compute='_compute_admin_stats', string='Total Courses')
    total_revenue = fields.Float(compute='_compute_admin_stats', string='Total Revenue')

    @api.depends('id')
    def _compute_related_records(self):
        for admin in self:
            admin.academic_year_ids = self.env['lms.academic.year'].search([('admin_id', '=', admin.id)])
            admin.semester_ids = self.env['lms.semester'].search([('admin_id', '=', admin.id)])
            admin.student_ids = self.env['lms.student'].search([('admin_id', '=', admin.id)])
            admin.teacher_ids = self.env['lms.teacher'].search([('admin_id', '=', admin.id)])
            admin.revenue_ids = self.env['lms.payment'].search([('admin_id', '=', admin.id), ('state', '=', 'paid')])
            admin.pending_payment_ids = self.env['lms.payment'].search([('admin_id', '=', admin.id), ('state', '=', 'pending')])

    @api.depends('student_ids', 'teacher_ids', 'revenue_ids')
    def _compute_admin_stats(self):
        for admin in self:
            # Count total students
            admin.total_student_count = len(admin.student_ids)

            # Count total teachers
            admin.total_teacher_count = len(admin.teacher_ids)

            # Count total courses
            admin.total_course_count = len(admin.student_ids.mapped('enrolled_courses'))

            # Calculate total revenue
            admin.total_revenue = sum(admin.revenue_ids.mapped('amount'))

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': 'Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('is_student', '=', True), ('admin_id', '=', self.id)],
            'context': {'default_is_student': True, 'default_admin_id': self.id},
        }

    def action_view_teachers(self):
        self.ensure_one()
        return {
            'name': 'Teachers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('is_teacher', '=', True), ('admin_id', '=', self.id)],
            'context': {'default_is_teacher': True, 'default_admin_id': self.id},
        }

    def action_view_courses(self):
        self.ensure_one()
        return {
            'name': 'Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'tree,form',
            'domain': [('admin_id', '=', self.id)],
            'context': {'default_admin_id': self.id},
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment',
            'view_mode': 'tree,form',
            'domain': [('admin_id', '=', self.id)],
            'context': {'default_admin_id': self.id},
        }

    def action_generate_student_report(self):
        self.ensure_one()
        return {
            'name': 'Student Report',
            'type': 'ir.actions.act_url',
            'url': '/web/export/student_report/%s' % self.id,
            'target': 'self',
        }

    def action_generate_teacher_report(self):
        self.ensure_one()
        return {
            'name': 'Teacher Report',
            'type': 'ir.actions.act_url',
            'url': '/web/export/teacher_report/%s' % self.id,
            'target': 'self',
        }

    def action_generate_financial_report(self):
        self.ensure_one()
        return {
            'name': 'Financial Report',
            'type': 'ir.actions.act_url',
            'url': '/web/export/financial_report/%s' % self.id,
            'target': 'self',
        }

    def action_generate_attendance_report(self):
        self.ensure_one()
        return {
            'name': 'Attendance Report',
            'type': 'ir.actions.act_url',
            'url': '/web/export/attendance_report/%s' % self.id,
            'target': 'self',
        }

    def action_create_academic_year(self):
        self.ensure_one()
        return {
            'name': 'Create Academic Year',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.academic.year',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admin_id': self.id,
                'default_state': 'draft'
            }
        }

    def action_create_semester(self):
        self.ensure_one()
        return {
            'name': 'Create Semester',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.semester',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admin_id': self.id,
                'default_state': 'draft'
            }
        }

    def action_bulk_enroll_students(self):
        self.ensure_one()
        return {
            'name': 'Bulk Enroll Students',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.bulk.enrollment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_admin_id': self.id,
                'default_state': 'draft'
            }
        }

    def action_manage_payment_plans(self):
        self.ensure_one()
        return {
            'name': 'Manage Payment Plans',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment.plan',
            'view_mode': 'tree,form',
            'domain': [('admin_id', '=', self.id)],
            'context': {'default_admin_id': self.id},
        }

    @api.constrains('administrator_code')
    def _check_administrator_code(self):
        for admin in self:
            if self.search_count([('administrator_code', '=', admin.administrator_code), ('id', '!=', admin.id)]) > 0:
                raise ValidationError("Administrator Code must be unique!") 