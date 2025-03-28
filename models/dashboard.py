from odoo import models, fields, api

class LMSDashboard(models.Model):
    _name = 'lms.dashboard'
    _description = 'LMS Dashboard'

    name = fields.Char(string='Dashboard Name', default='LMS Dashboard')
    color = fields.Integer(string='Color Index')
    student_count = fields.Integer(compute='_compute_counts')
    course_count = fields.Integer(compute='_compute_counts')
    enrollment_count = fields.Integer(compute='_compute_counts')
    pending_payment_count = fields.Integer(compute='_compute_counts')
    active_student_count = fields.Integer(compute='_compute_counts')
    teacher_count = fields.Integer(compute='_compute_counts')
    upcoming_class_count = fields.Integer(compute='_compute_counts')
    recent_enrollments = fields.Many2many('lms.enrollment', compute='_compute_recent_enrollments')
    popular_courses = fields.Many2many('slide.channel', compute='_compute_popular_courses')

    @api.depends()
    def _compute_counts(self):
        for record in self:
            record.student_count = self.env['res.users'].search_count([('is_student', '=', True)])
            record.course_count = self.env['slide.channel'].search_count([])
            record.enrollment_count = self.env['lms.enrollment'].search_count([])
            record.pending_payment_count = self.env['lms.enrollment'].search_count([('payment_status', '=', 'pending')])
            record.active_student_count = self.env['res.users'].search_count([('is_student', '=', True), ('active', '=', True)])
            record.teacher_count = self.env['res.users'].search_count([('is_teacher', '=', True)])
            # Calculate upcoming classes - depends on your implementation
            record.upcoming_class_count = self.env['lms.course.planning'].search_count([
                ('date', '>=', fields.Date.today())
            ])

    @api.depends()
    def _compute_recent_enrollments(self):
        for record in self:
            record.recent_enrollments = self.env['lms.enrollment'].search(
                [], order='enrollment_date desc', limit=5
            )

    @api.depends()
    def _compute_popular_courses(self):
        for record in self:
            record.popular_courses = self.env['slide.channel'].search(
                [], order='student_count desc', limit=5
            )
    
    # Action methods for dashboard
    def action_view_students(self):
        return {
            'name': 'Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'kanban,tree,form',
            'domain': [('is_student', '=', True)],
        }
    
    def action_view_courses(self):
        return {
            'name': 'Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'kanban,tree,form',
        }
    
    def action_view_enrollments(self):
        return {
            'name': 'Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'kanban,tree,form',
        }
    
    def action_view_teachers(self):
        return {
            'name': 'Teachers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'kanban,tree,form',
            'domain': [('is_teacher', '=', True)],
        }
    
    def action_view_pending_payments(self):
        return {
            'name': 'Pending Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('payment_status', '=', 'pending')],
        }
    
    def action_view_active_students(self):
        return {
            'name': 'Active Students',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'kanban,tree,form',
            'domain': [('is_student', '=', True), ('active', '=', True)],
        }
    
    def action_view_upcoming_classes(self):
        return {
            'name': 'Upcoming Classes',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.course.planning',
            'view_mode': 'calendar,tree,form',
            'domain': [('date', '>=', fields.Date.today())],
        }
    
    def action_new_student(self):
        return {
            'name': 'New Student',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_is_student': True},
        }
    
    def action_new_course(self):
        return {
            'name': 'New Course',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_new_enrollment(self):
        return {
            'name': 'New Enrollment',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_new_payment(self):
        return {
            'name': 'New Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.payment',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def _ensure_dashboard_exists(self):
        """Ensure at least one dashboard record exists"""
        dashboard = self.search([], limit=1)
        if not dashboard:
            self.create({'name': 'LMS Dashboard'}) 