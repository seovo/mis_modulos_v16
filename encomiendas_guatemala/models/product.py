from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_encomienda = fields.Boolean(string="Es un Producto Encomienda")
    price_extra_libre = fields.Float(string="Precio Extra Libra")