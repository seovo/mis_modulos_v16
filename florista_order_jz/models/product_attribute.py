from odoo import _, api, fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    is_period_florista = fields.Boolean(string='Es Periodo Flores')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    is_period_florista = fields.Boolean(related='attribute_id.is_period_florista')
    number_period_florista = fields.Integer(string="Nro Periodo")
    interval_period_florista = fields.Integer(string="Dias Intervalo")