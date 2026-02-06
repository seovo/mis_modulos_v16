from odoo import api, fields, models, _


class Product_Template_H(models.Model):
    _inherit = 'product.template'

    type_exist = fields.Many2one('catalog.element', string="Tipo de Existencia", domain=[('table_id.code', '=', 'PE.SUNAT.PLE_TABLE05')])
    catalog_exist = fields.Many2one('catalog.element', string="Catalogo de existencia", domain=[('table_id.code', '=', 'PE.SUNAT.PLE_TABLE13')])
