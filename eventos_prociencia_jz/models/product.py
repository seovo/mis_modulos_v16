from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_product_event = fields.Boolean(string='Producto Evento')
    margin_stock_danger = fields.Integer(string="Margen Stock Rojo")
    margin_stock_warning = fields.Integer(string="Margen Stock Amarillo")