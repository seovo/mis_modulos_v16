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

    count_lot_sale = fields.Integer(compute='get_count_lot')
    count_lot_separate = fields.Integer(compute='get_count_lot')
    count_lot_free = fields.Integer(compute='get_count_lot')

    def get_count_lot(self):
        for record in self:
            count_sale = 0
            count_separate = 0
            count_free = 0
            for line in record.report_lot_land_line_ids:
                if line.state == 'sale':
                    count_sale += 1

                if line.state == 'separate':
                    count_separate += 1

                if line.state == 'free':
                    count_free += 1


            record.count_lot_sale = count_sale
            record.count_lot_separate = count_separate
            record.count_lot_free = count_free


