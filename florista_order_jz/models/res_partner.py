from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')