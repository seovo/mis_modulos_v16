from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    series_available_factu_jz = fields.Char(string='Series Permitidas')
    automatic_factu_jz = fields.Boolean(default=True,string='Facturar Automaticamente')