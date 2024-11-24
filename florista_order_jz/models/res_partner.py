from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')
    until_hour_florista = fields.Many2one('until.hour.florista', string="Entregar Hasta")


