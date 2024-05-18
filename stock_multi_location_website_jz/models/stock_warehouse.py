from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'stock.warehouse'
    show_stock_website_jz = fields.Boolean(string="Mostrar Stock en Sitio Web")
