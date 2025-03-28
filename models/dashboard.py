from odoo import api, fields, models
from odoo.exceptions import UserError

class LmsDashboard(models.Model):
    _name = 'lms.dashboard'
    _description = 'LMS Dashboard'
    
    name = fields.Char(string='Name', default='Dashboard')
    active = fields.Boolean(default=True)
    
    def open_assignments(self):
        """Open assignments view for current user"""
        self.ensure_one()
        # This is just a placeholder - replace with actual action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignments',
            'res_model': 'lms.assignment',
            'view_mode': 'kanban,tree,form',
            'domain': [],
            'context': {'search_default_my_assignments': 1},
        }
    
    def open_grades(self):
        """Open grades view for current user"""
        self.ensure_one()
        # This is just a placeholder - replace with actual action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Grades',
            'res_model': 'lms.grade',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {'search_default_my_grades': 1},
        }
    
    @api.model
    def get_dashboard_data(self):
        """Get data for dashboard"""
        user = self.env.user
        
        # Get courses the user is enrolled in or teaching
        courses = []
        if user.is_student:
            course_ids = user.enrolled_courses.ids
            courses = self.env['slide.channel'].browse(course_ids).read(['name', 'image_128'])
        elif user.is_teacher:
            course_ids = user.course_assignment_ids.mapped('course_id').ids
            courses = self.env['slide.channel'].browse(course_ids).read(['name', 'image_128'])
        
        # Get upcoming assignments
        assignments = []
        if hasattr(self.env, 'lms.assignment'):
            assignment_model = self.env['lms.assignment']
            if user.is_student:
                assignments = assignment_model.search([
                    ('student_id', '=', user.id),
                    ('state', 'in', ['draft', 'submitted']),
                ], limit=5).read(['name', 'deadline', 'state'])
            elif user.is_teacher:
                assignments = assignment_model.search([
                    ('teacher_id', '=', user.id),
                ], limit=5).read(['name', 'deadline', 'state'])
        
        # Get announcements
        announcements = []
        if hasattr(self.env, 'lms.announcement'):
            announcement_model = self.env['lms.announcement']
            announcements = announcement_model.search([], limit=5).read(['name', 'date', 'message'])
        
        return {
            'courses': courses,
            'assignments': assignments,
            'announcements': announcements,
        } 