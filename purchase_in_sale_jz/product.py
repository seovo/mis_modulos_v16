from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_product_purchase = fields.Boolean(string='Producto Compra')