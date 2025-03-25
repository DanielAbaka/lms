from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64

class CourseMaterial(models.Model):
    _name = 'lms.course.material'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Course Material'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Html(string='Description')
    course_id = fields.Many2one('lms.course', string='Course', required=True, tracking=True)
    teacher_id = fields.Many2one('lms.teacher', string='Uploaded By', 
                                default=lambda self: self.env.user.teacher_id)
    
    # Content Type and Storage
    material_type = fields.Selection([
        ('document', 'Document'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('quiz', 'Quiz'),
        ('presentation', 'Presentation'),
        ('other', 'Other')
    ], required=True, default='document', tracking=True)
    
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    file_size = fields.Float(string='File Size (MB)', compute='_compute_file_size', store=True)
    url = fields.Char(string='URL')
    content = fields.Html(string='Content')
    
    # Access Control
    is_published = fields.Boolean(string='Published', default=False, tracking=True)
    publish_date = fields.Datetime(string='Publish Date')
    access_limit = fields.Selection([
        ('all', 'All Enrolled Students'),
        ('groups', 'Specific Groups'),
        ('individual', 'Individual Students')
    ], default='all', string='Access Limitation')
    allowed_group_ids = fields.Many2many('lms.student.group', string='Allowed Groups')
    allowed_student_ids = fields.Many2many('lms.student', string='Allowed Students')
    
    # Tracking
    view_count = fields.Integer(string='Views', default=0)
    download_count = fields.Integer(string='Downloads', default=0)
    last_viewed = fields.Datetime(string='Last Viewed')
    
    # Dependencies
    prerequisite_material_ids = fields.Many2many(
        'lms.course.material',
        'material_prerequisite_rel',
        'material_id',
        'prerequisite_id',
        string='Prerequisites'
    )

    @api.depends('file')
    def _compute_file_size(self):
        for record in self:
            if record.file:
                file_content = base64.b64decode(record.file)
                record.file_size = len(file_content) / (1024 * 1024)  # Convert to MB
            else:
                record.file_size = 0

    @api.constrains('material_type', 'file', 'url', 'content')
    def _check_content(self):
        for record in self:
            if record.material_type == 'document' and not record.file:
                raise ValidationError('Document type requires a file upload.')
            elif record.material_type == 'video' and not (record.file or record.url):
                raise ValidationError('Video type requires either a file upload or URL.')
            elif record.material_type == 'link' and not record.url:
                raise ValidationError('Link type requires a URL.')

    def action_publish(self):
        self.write({
            'is_published': True,
            'publish_date': fields.Datetime.now()
        })

    def action_unpublish(self):
        self.write({'is_published': False})

    def action_view_statistics(self):
        self.ensure_one()
        return {
            'name': 'Material Statistics',
            'type': 'ir.actions.act_window',
            'res_model': 'lms.material.statistics',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_material_id': self.id}
        }

    def track_view(self, student_id):
        self.ensure_one()
        self.write({
            'view_count': self.view_count + 1,
            'last_viewed': fields.Datetime.now()
        })
        # Create view log
        self.env['lms.material.view.log'].create({
            'material_id': self.id,
            'student_id': student_id,
            'view_datetime': fields.Datetime.now()
        })

    def track_download(self, student_id):
        self.ensure_one()
        self.write({'download_count': self.download_count + 1})
        # Create download log
        self.env['lms.material.download.log'].create({
            'material_id': self.id,
            'student_id': student_id,
            'download_datetime': fields.Datetime.now()
        })

    @api.model
    def create(self, vals):
        # Additional validation and processing
        if vals.get('material_type') == 'document':
            # Check file extension
            if vals.get('file_name'):
                allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']
                if not any(vals['file_name'].lower().endswith(ext) for ext in allowed_extensions):
                    raise ValidationError('Invalid file type. Allowed types: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX')
        
        return super(CourseMaterial, self).create(vals)

    def write(self, vals):
        # Track changes to published materials
        if 'is_published' in vals and vals['is_published']:
            vals['publish_date'] = fields.Datetime.now()
        return super(CourseMaterial, self).write(vals)

    def unlink(self):
        # Prevent deletion of published materials
        for record in self:
            if record.is_published:
                raise ValidationError('Cannot delete published materials.')
        return super(CourseMaterial, self).unlink()

    @api.onchange('file')
    def _onchange_file(self):
        if self.file:
            self.file_name = self.file_name or f"{self.name}.pdf" 