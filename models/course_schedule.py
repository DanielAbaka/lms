from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class CourseSchedule(models.Model):
    _name = 'lms.course.schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Course Schedule'
    _order = 'day_of_week,start_time'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    course_id = fields.Many2one('lms.course', string='Course', required=True, tracking=True)
    teacher_id = fields.Many2one('lms.teacher', string='Teacher', tracking=True)
    room_id = fields.Many2one('lms.classroom', string='Classroom', tracking=True)
    
    # Schedule Details
    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], required=True, tracking=True)
    
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    
    # Recurrence
    is_recurring = fields.Boolean(string='Recurring', default=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    
    # Additional Information
    capacity = fields.Integer(string='Room Capacity', related='room_id.capacity')
    enrolled_count = fields.Integer(string='Enrolled Count')
    
    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for schedule in self:
            if schedule.start_time >= schedule.end_time:
                raise ValidationError('End time must be after start time') 