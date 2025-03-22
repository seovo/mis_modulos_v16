from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    token_whatsapp_evolution_api = fields.Char(string="Token Whatsapp")
    url_whatsapp_evolution_api = fields.Char(string="Url Whatsapp")