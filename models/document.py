from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Document(models.Model):
    _name = 'lms.document'
    _description = 'Course Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name'

    name = fields.Char(string='Name', required=True, tracking=True)
    teacher_assignment_id = fields.Many2one('lms.teacher.assignment', string='Teacher Assignment', required=True)
    course_id = fields.Many2one('slide.channel', string='Course', related='teacher_assignment_id.course_id', store=True)
    academic_year_id = fields.Many2one('lms.academic.year', string='Academic Year',
                                       related='teacher_assignment_id.academic_year_id', store=True)
    semester_id = fields.Many2one('lms.semester', string='Semester',
                                  related='teacher_assignment_id.semester_id', store=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    file = fields.Binary(string='File', required=True, attachment=True)
    file_name = fields.Char(string='File Name', required=True)
    file_type = fields.Selection([
        ('pdf', 'PDF'),
        ('doc', 'Word'),
        ('xls', 'Excel'),
        ('ppt', 'PowerPoint'),
        ('txt', 'Text'),
        ('other', 'Other')
    ], string='File Type', compute='_compute_file_type', store=True)
    file_size = fields.Integer(string='File Size (bytes)', compute='_compute_file_size', store=True)
    is_public = fields.Boolean(string='Public Access', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    access_log_ids = fields.One2many('lms.document.access', 'document_id', string='Access Logs')

    # Statistics
    access_count = fields.Integer(string='Access Count', compute='_compute_statistics', store=True)
    download_count = fields.Integer(string='Download Count', compute='_compute_statistics', store=True)
    last_accessed = fields.Datetime(string='Last Accessed', compute='_compute_statistics', store=True)

    @api.depends('file_name')
    def _compute_file_type(self):
        for record in self:
            if record.file_name:
                ext = record.file_name.split('.')[-1].lower()
                if ext in ['pdf']:
                    record.file_type = 'pdf'
                elif ext in ['doc', 'docx']:
                    record.file_type = 'doc'
                elif ext in ['xls', 'xlsx']:
                    record.file_type = 'xls'
                elif ext in ['ppt', 'pptx']:
                    record.file_type = 'ppt'
                elif ext in ['txt']:
                    record.file_type = 'txt'
                else:
                    record.file_type = 'other'

    @api.depends('file')
    def _compute_file_size(self):
        for record in self:
            record.file_size = len(record.file) if record.file else 0

    @api.depends('access_log_ids', 'access_log_ids.access_type')
    def _compute_statistics(self):
        for record in self:
            record.access_count = len(record.access_log_ids)
            record.download_count = len(record.access_log_ids.filtered(lambda x: x.access_type == 'download'))
            if record.access_log_ids:
                record.last_accessed = max(record.access_log_ids.mapped('access_date'))
            else:
                record.last_accessed = False

    def action_publish(self):
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'published'})

    def action_archive(self):
        self.ensure_one()
        if self.state == 'published':
            self.write({'state': 'archived'})

    def action_unarchive(self):
        self.ensure_one()
        if self.state == 'archived':
            self.write({'state': 'published'})

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state in ['published', 'archived']:
            self.write({'state': 'draft'})

    def log_access(self, user_id):
        self.ensure_one()
        self.env['lms.document.access'].create({
            'document_id': self.id,
            'user_id': user_id,
            'access_date': fields.Datetime.now()
        })