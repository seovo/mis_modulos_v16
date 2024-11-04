from odoo import api, fields, models

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    user_id = fields.Many2one(string="Cajero")