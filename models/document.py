from odoo import models, fields, api

class LMSDocument(models.Model):
    """
    A custom LMS Document record that links to an existing attachment_id.
    The user can pick an existing attachment or create a new one separately.
    """
    _name = 'lms.document'
    _description = 'LMS Document (Using ir.attachment)'

    name = fields.Char(string="Document Name", required=True)
    course_id = fields.Many2one('slide.channel', string="Course")
    attachment_id = fields.Many2one(
        'ir.attachment', 
        string="Attachment",
        help="Select an existing attachment or create one via the chatter in another record."
    )
    description = fields.Text(string="Description")

    # If you want to automatically create a new attachment from a file,
    # you’d need additional logic or a wizard to do so.