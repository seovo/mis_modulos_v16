from odoo import _, api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    product_florista_ids = fields.One2many('product.product.florista','product_id')


class ProductProductFlorista(models.Model):
    _name = 'product.product.florista'
    sequence = fields.Integer()
    product_id = fields.Many2one('product.product')
    product_terminado_id = fields.Many2one('product.product',string="Producto Terminado")



class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    is_period_florista = fields.Boolean(string='Es Periodo Flores')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    is_period_florista = fields.Boolean(related='attribute_id.is_period_florista')
    number_period_florista = fields.Integer(string="Nro Periodo")
    interval_period_florista = fields.Integer(string="Dias Intervalo")