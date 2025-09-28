from odoo import fields, models

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    is_default_without_company = fields.Boolean(string="Por Defecto sin Compañia")
