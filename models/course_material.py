from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CourseMaterial(models.Model):
    _name = 'lms.course.material'
    _description = 'Course Material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Title', required=True, tracking=True)
    course_id = fields.Many2one('slide.channel', string='Course', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    material_type = fields.Selection([
        ('document', 'Document'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('link', 'External Link')
    ], string='Material Type', required=True, tracking=True)
    description = fields.Html(string='Description', tracking=True)
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    video_url = fields.Char(string='Video URL')
    external_url = fields.Char(string='External URL')
    duration = fields.Float(string='Duration (minutes)', help='Duration for video content')
    due_date = fields.Datetime(string='Due Date', help='Due date for assignments and quizzes')
    max_score = fields.Float(string='Maximum Score', help='Maximum score for quizzes and assignments')
    is_published = fields.Boolean(string='Published', default=False, tracking=True)
    published_date = fields.Datetime(string='Published Date', readonly=True)
    published_by = fields.Many2one('res.users', string='Published By', readonly=True)
    student_ids = fields.Many2many('res.users', 'student_material_rel', 'material_id', 'student_id', 
                                 string='Students', domain=[('is_student', '=', True)])
    teacher_ids = fields.Many2many('res.users', 'teacher_material_rel', 'material_id', 'teacher_id', 
                                 string='Teachers', domain=[('is_teacher', '=', True)])
    view_count = fields.Integer(string='View Count', compute='_compute_view_count', store=True)
    last_viewed = fields.Datetime(string='Last Viewed', compute='_compute_view_count', store=True)
    category = fields.Selection([
        ('lecture', 'Lecture Material'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('resource', 'Additional Resource'),
        ('announcement', 'Announcement')
    ], string='Category', required=True, default='lecture', tracking=True)
    tags = fields.Many2many('lms.material.tag', string='Tags')
    is_required = fields.Boolean(string='Required', default=False, tracking=True)
    prerequisites = fields.Many2many('lms.course.material', 'material_prerequisite_rel', 
                                   'material_id', 'prerequisite_id', string='Prerequisites')

    @api.depends('student_ids')
    def _compute_view_count(self):
        for material in self:
            material.view_count = len(material.student_ids)
            if material.student_ids:
                material.last_viewed = fields.Datetime.now()

    def action_publish(self):
        self.ensure_one()
        if not self.is_published:
            self.write({
                'is_published': True,
                'published_date': fields.Datetime.now(),
                'published_by': self.env.user.id
            })

    def action_unpublish(self):
        self.ensure_one()
        if self.is_published:
            self.write({
                'is_published': False,
                'published_date': False,
                'published_by': False
            })

    def action_view_submissions(self):
        self.ensure_one()
        return {
            'name': 'Material Submissions',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.material.submission',
            'view_mode': 'tree,form',
            'domain': [('material_id', '=', self.id)],
            'context': {'default_material_id': self.id},
        }

    @api.constrains('due_date')
    def _check_due_date(self):
        for record in self:
            if record.due_date and record.due_date < fields.Datetime.now():
                raise ValidationError("Due date cannot be in the past!")

    @api.constrains('max_score')
    def _check_max_score(self):
        for record in self:
            if record.max_score < 0:
                raise ValidationError("Maximum score cannot be negative!")

    @api.constrains('duration')
    def _check_duration(self):
        for record in self:
            if record.duration < 0:
                raise ValidationError("Duration cannot be negative!")


class MaterialTag(models.Model):
    _name = 'lms.material.tag'
    _description = 'Course Material Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    material_ids = fields.Many2many('lms.course.material', string='Materials') 