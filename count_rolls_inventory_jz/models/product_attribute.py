from odoo import api, fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    type_rolls = fields.Selection([('cat','Categoria'),('model','Modelo'),('color','Color')])

    def write(self,vals):
        res = super().write(vals)
        #raise ValueError(vals)

        for record in self:
            atributos = self.env['product.template.attribute.line'].search([('attribute_id', '=',record.id)])
            for attr in atributos:
                for line in record.value_ids:
                    if line.id not in attr.value_ids.ids:
                        attr.value_ids  =  [(4, line.id)]


        return res

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'
    product_template_attribute_value_id = fields.Many2one('product.template.attribute.value',
                                                          # domain=[('attribute_line_id','=',attribute_line_id)],
                                                          string="Valor Parent"
                                                          )