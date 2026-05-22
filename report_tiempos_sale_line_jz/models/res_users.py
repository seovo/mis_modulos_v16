from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'
    company_rstk_ids = fields.Many2many('res.company', string="Compañias Reporte Sensotek Adicional")
    partner_rstk_ids = fields.Many2many('res.partner', string="Contactos Reporte Sensotek Adicional")
