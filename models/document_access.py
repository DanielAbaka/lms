from odoo import models, fields, api


class DocumentAccess(models.Model):
    _name = 'lms.document.access'
    _description = 'Document Access Log'
    _order = 'access_date desc'

    document_id = fields.Many2one('lms.document', string='Document', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    access_date = fields.Datetime(string='Access Date', required=True, default=fields.Datetime.now)
    ip_address = fields.Char(string='IP Address')
    user_agent = fields.Char(string='User Agent')
    duration = fields.Integer(string='Duration (seconds)')
    is_downloaded = fields.Boolean(string='Downloaded', default=False)
    notes = fields.Text(string='Notes') 