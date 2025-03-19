from odoo import models, fields

class LMSPayment(models.Model):
    _inherit = 'payment.transaction'

    enrollment_id = fields.Many2one('lms.enrollment', string="Enrollment")