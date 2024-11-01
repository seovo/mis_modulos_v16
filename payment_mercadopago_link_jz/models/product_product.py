from odoo import _, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    link_mercado_pago = fields.Char(string="Link Mercado Pago")