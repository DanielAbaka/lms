from odoo import models, fields

class LMSMessaging(models.Model):
    """
    A custom messaging model that inherits mail.thread
    so it can track messages/activities in Odoo's chatter.
    """
    _name = 'lms.messaging'
    _description = 'LMS Messaging'
    _inherit = 'mail.thread'  # Inherits chatter functionality

    message_content = fields.Text(string="Message Content")
    sender_id = fields.Many2one('res.users', string="Sender")
    recipient_ids = fields.Many2many('res.users', string="Recipients")