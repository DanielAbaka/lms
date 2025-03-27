from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ScheduleTemplate(models.Model):
    _name = 'lms.schedule.template'
    _description = 'Schedule Template'

    name = fields.Char(string='Name', required=True)
    admin_id = fields.Many2one('res.users', string='Administrator', domain=[('is_admin', '=', True)])
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True)
    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Day of Week', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    classroom = fields.Char(string='Classroom', required=True)
    capacity = fields.Integer(string='Capacity', required=True)
    teacher_assignment_ids = fields.One2many('lms.teacher.assignment', 'schedule_template_id', string='Teacher Assignments')

    @api.constrains('start_time', 'end_time')
    def _check_time(self):
        for record in self:
            if record.end_time <= record.start_time:
                raise ValidationError(_('End time must be after start time'))


class ScheduleBulkWizard(models.TransientModel):
    _name = 'lms.schedule.bulk.wizard'
    _description = 'Bulk Schedule Creation Wizard'

    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True)
    template_id = fields.Many2one('lms.schedule.template', string='Template', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    classroom = fields.Char(string='Classroom', required=True)
    teacher_id = fields.Many2one('res.users', string='Teacher', domain=[('is_teacher', '=', True)])

    def action_create_schedules(self):
        self.ensure_one()
        schedules = []
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.strftime('%A').lower() == self.template_id.day_of_week:
                schedule_vals = {
                    'name': f"{self.template_id.course_id.name} - {current_date.strftime('%Y-%m-%d')}",
                    'academic_year_id': self.academic_year_id.id,
                    'semester_id': self.semester_id.id,
                    'course_id': self.template_id.course_id.id,
                    'day_of_week': self.template_id.day_of_week,
                    'start_time': self.template_id.start_time,
                    'end_time': self.template_id.end_time,
                    'classroom': self.classroom,
                    'capacity': self.template_id.capacity,
                    'date': current_date,
                }
                schedules.append(schedule_vals)
            current_date += timedelta(days=1)

        created_schedules = self.env['lms.schedule'].create(schedules)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Schedules'),
            'res_model': 'lms.schedule',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created_schedules.ids)],
        }


class RoomAvailabilityWizard(models.TransientModel):
    _name = 'lms.room.availability.wizard'
    _description = 'Room Availability Check Wizard'

    classroom = fields.Char(string='Classroom', required=True)
    date = fields.Date(string='Date', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    available_rooms = fields.One2many('lms.room.availability', 'wizard_id', string='Available Rooms')

    @api.onchange('classroom', 'date', 'start_time', 'end_time')
    def _onchange_room_availability(self):
        if not all([self.classroom, self.date, self.start_time, self.end_time]):
            return

        # Get conflicting schedules
        conflicting_schedules = self.env['lms.schedule'].search([
            ('classroom', '=', self.classroom),
            ('date', '=', self.date),
            '|',
            '&',
            ('start_time', '<=', self.start_time),
            ('end_time', '>', self.start_time),
            '&',
            ('start_time', '<', self.end_time),
            ('end_time', '>=', self.end_time),
        ])

        # Create availability records
        self.available_rooms = [(0, 0, {
            'name': self.classroom,
            'capacity': 30,  # Default capacity, can be made configurable
            'is_available': not bool(conflicting_schedules),
            'conflicting_schedules': ', '.join(conflicting_schedules.mapped('name')),
        })]


class RoomAvailability(models.TransientModel):
    _name = 'lms.room.availability'
    _description = 'Room Availability'

    wizard_id = fields.Many2one('lms.room.availability.wizard', string='Wizard')
    name = fields.Char(string='Room Name')
    capacity = fields.Integer(string='Capacity')
    is_available = fields.Boolean(string='Available')
    conflicting_schedules = fields.Char(string='Conflicting Schedules')


class Schedule(models.Model):
    _name = 'lms.schedule'
    _description = 'Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, start_time'

    name = fields.Char(string='Name', required=True, tracking=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year', required=True, tracking=True)
    semester_id = fields.Many2one('lms.semester', string='Semester', required=True, tracking=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True, tracking=True)
    teacher_assignment_id = fields.Many2one('lms.teacher.assignment', string='Teacher Assignment', required=True, tracking=True)
    
    # Schedule Details
    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Day of Week', required=True, tracking=True)
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)
    classroom = fields.Char(string='Classroom', required=True, tracking=True)
    capacity = fields.Integer(string='Capacity', required=True, tracking=True)
    date = fields.Date(string='Date', required=True, tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # Related Records
    attendance_ids = fields.One2many('lms.attendance', 'schedule_id', string='Attendance Records')
    enrollment_ids = fields.One2many('lms.enrollment', 'schedule_id', string='Enrollments')

    # Computed Fields
    enrolled_students_count = fields.Integer(string='Enrolled Students', compute='_compute_enrollment_count', store=True)
    available_slots = fields.Integer(string='Available Slots', compute='_compute_available_slots', store=True)
    is_full = fields.Boolean(string='Is Full', compute='_compute_is_full', store=True)
    teacher_assignment_count = fields.Integer(string='Teacher Assignments', compute='_compute_teacher_assignment_count', store=True)

    @api.depends('teacher_assignment_id')
    def _compute_teacher_assignment_count(self):
        for record in self:
            record.teacher_assignment_count = 1 if record.teacher_assignment_id else 0

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for record in self:
            record.enrolled_students_count = len(record.enrollment_ids)

    @api.depends('capacity', 'enrolled_students_count')
    def _compute_available_slots(self):
        for record in self:
            record.available_slots = record.capacity - record.enrolled_students_count

    @api.depends('available_slots')
    def _compute_is_full(self):
        for record in self:
            record.is_full = record.available_slots <= 0

    @api.constrains('start_time', 'end_time')
    def _check_time(self):
        for record in self:
            if record.end_time <= record.start_time:
                raise ValidationError(_('End time must be after start time'))

    @api.constrains('teacher_assignment_id', 'date', 'start_time', 'end_time')
    def _check_teacher_availability(self):
        for record in self:
            conflicting_schedules = self.env['lms.schedule'].search([
                ('id', '!=', record.id),
                ('teacher_assignment_id', '=', record.teacher_assignment_id.id),
                ('date', '=', record.date),
                '|',
                '&',
                ('start_time', '<=', record.start_time),
                ('end_time', '>', record.start_time),
                '&',
                ('start_time', '<', record.end_time),
                ('end_time', '>=', record.end_time),
            ])
            if conflicting_schedules:
                raise ValidationError(_('Teacher is already assigned to another class during this time'))

    def action_activate(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'active'})

    def action_complete(self):
        self.ensure_one()
        if self.state == 'active':
            self.write({'state': 'completed'})

    def action_cancel(self):
        self.ensure_one()
        if self.state in ['draft', 'active']:
            self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state == 'cancelled':
            self.write({'state': 'draft'})

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'name': 'Attendance Records',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.attendance',
            'view_mode': 'tree,form',
            'domain': [('schedule_id', '=', self.id)],
            'context': {'default_schedule_id': self.id},
        }

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            'name': 'Enrollments',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.enrollment',
            'view_mode': 'tree,form',
            'domain': [('schedule_id', '=', self.id)],
            'context': {'default_schedule_id': self.id},
        }

    def action_bulk_create(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Schedule Creation'),
            'res_model': 'lms.schedule.bulk.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_check_room_availability(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Check Room Availability'),
            'res_model': 'lms.room.availability.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_classroom': self.classroom,
                'default_date': self.date,
                'default_start_time': self.start_time,
                'default_end_time': self.end_time,
            }
        } 