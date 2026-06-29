from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    marca = fields.Char()
    modelo = fields.Char()
    serie  = fields.Char()
    nombre_corto = fields.Char()

