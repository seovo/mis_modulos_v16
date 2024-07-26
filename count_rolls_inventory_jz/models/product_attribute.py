from odoo import api, fields, models

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'
    product_template_attribute_value_id = fields.Many2one('product.template.attribute.value',
                                                          # domain=[('attribute_line_id','=',attribute_line_id)],
                                                          string="Valor Parent"
                                                          )