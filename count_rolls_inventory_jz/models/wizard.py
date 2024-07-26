from odoo import api, fields, models
import datetime

class ProductWizardVariant(models.TransientModel):
    _name = "product.wizard.variant"
    _description  = "product.wizard.variant"
    product       = fields.Many2one('product.template')
    line_ids      = fields.One2many('product.wizard.variant.line','parent_id')
    sale_id       = fields.Many2one('sale.order')

    @api.onchange('sale_id')
    def change_salex(self):
        pt = self.env['product.template'].search([('attribute_line_ids','!=',False)],limit=1)
        if pt:
            self.product = pt.id



    @api.onchange('product')
    def change_product(self):
        self.line_ids = False
        if self.product:
            if self.product.attribute_line_ids:
                line_attribute_id = False
                for line in self.product.attribute_line_ids:

                    self.line_ids += self.env['product.wizard.variant.line'].new({
                        'attribute_line_id': line.id
                    })

                    if line.attribute_id.type_rolls == 'cat':
                        line_attribute_id = line
                    if line_attribute_id and    line.attribute_id.type_rolls == 'model':
                        line.product_template_attribute_value_filter = line_attribute_id.id
                    #type_rolls

    def add_product(self):
        return


class ProductWizardVariantLine(models.TransientModel):
    _name = "product.wizard.variant.line"
    _description = "product.wizard.variant.line"
    parent_id = fields.Many2one("product.wizard.variant")
    attribute_line_id = fields.Many2one('product.template.attribute.line',string="Atributo")
    product_template_attribute_value_id = fields.Many2one('product.template.attribute.value',
                                                          #domain=[('attribute_line_id','=',attribute_line_id)],
                                                          string="Valor"
                                                          )
    product_template_attribute_value_filter = fields.Many2one('product.template.attribute.value',
                                                          # domain=[('attribute_line_id','=',attribute_line_id)],
                                                          string="Valor"
                                                          )



