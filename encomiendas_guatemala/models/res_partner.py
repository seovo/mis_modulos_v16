from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit       = 'res.partner'
    use_whatsapp = fields.Boolean(string='Tiene Wasap')