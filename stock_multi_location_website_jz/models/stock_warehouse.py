from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'stock.warehouse'
    show_stock_website_jz = fields.Boolean(string="Mostrar Stock en Sitio Web")
    type_show_website_jz = fields.Selection([('hand','A mano'),('forecast','Pronosticado')],default='forecast',string="Tipo Stock a Mostrar en Sitio Web")
