from odoo import api, fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    type_land = fields.Selection([('stage','Etapa'),('lot','Lote'),('mz','Manzana'),('m2','M2')])

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


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    type_land = fields.Selection(related='attribute_id.type_land')
    value_land = fields.Float()

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'
    max_lot = fields.Integer(string='Cantidad Lotes')
    report_lot_land_line_ids = fields.One2many('report.lot.land.line', 'mz_value_id')


