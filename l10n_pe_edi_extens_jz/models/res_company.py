from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    token_apis_net_pe = fields.Char()