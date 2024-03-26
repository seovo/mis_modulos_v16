from odoo import api, fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    type_land = fields.Selection([('stage','Etapa'),('lot','Lote'),('mz','Manzana'),('m2','M2')])


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    type_land = fields.Selection(related='attribute_id.type_land')
    value_land = fields.Float()
