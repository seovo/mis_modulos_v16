from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_encomienda = fields.Boolean(string="Es un Producto Encomienda")
    is_tarif_encomienda = fields.Boolean(string="Es Tarifa Encomienda")
    price_extra_libre = fields.Float(string="Precio Extra Libra")
    largo_enc = fields.Float(string="Largo")
    alto_enc = fields.Float(string="Alto")
    ancho_enc = fields.Float(string="Largo")