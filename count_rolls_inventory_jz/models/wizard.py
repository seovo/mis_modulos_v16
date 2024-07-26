from odoo import api, fields, models
import datetime

class ProductWizardVariant(models.TransientModel):
    _name = "product.wizard.variant"
    _description  = "product.wizard.variant"
    product       = fields.Many2one('product.template',required=True)
    categ_id      = fields.Many2one('product.template.attribute.value',
                                    domain=[('attribute_id.type_rolls','=','cat')],
                                    string="Categoria",
                                    required=True
                                    )
    model_id = fields.Many2one('product.template.attribute.value',
                               string="Modelo",
                               required=True
                               )

    color_id = fields.Many2one('product.template.attribute.value',
                               domain=[('attribute_id.type_rolls', '=', 'color')],
                               string="Color",
                               required=True
                               )

    #line_ids      = fields.One2many('product.wizard.variant.line','parent_id')
    sale_id       = fields.Many2one('sale.order',required=True)

    def add_product(self):
        product = self.env['product.product'].search([
            ('product_tmpl_id','=',self.product.id),
            ('product_template_attribute_value_ids','=', [(6,0,[self.categ_id.id,self.model_id.id,self.color_id.id])])
        ])
        raise ValueError(product)

    @api.onchange('sale_id')
    def change_salex(self):
        pt = self.env['product.template'].search([('attribute_line_ids','!=',False)],limit=1)
        if pt:
            self.product = pt.id


    '''
    @api.onchange('product')
    def change_product(self):
        self.line_ids = False
        if self.product:
            if self.product.attribute_line_ids:

                for line in self.product.attribute_line_ids:

                    #if line.attribute_id.type_rolls == 'cat':
                    #    line_attribute = line

                    dx = {
                        'attribute_line_id': line.id
                    }

                    #if line_attribute and    line.attribute_id.type_rolls == 'model':
                    #    raise ValueError(line_attribute)
                    #    dx.update({
                    #        'product_template_attribute_value_filter': line_attribute.id
                    #    })


                    self.line_ids += self.env['product.wizard.variant.line'].new(dx)


                    #type_rolls
    '''


'''
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
                                                          string="Filtro"
                                                          )

    @api.onchange('product_template_attribute_value_id')
    def ch_product_template_attribute_value_id(self):
        for record in self:

            if record.attribute_line_id.attribute_id.type_rolls == 'cat':
                for line in record.parent_id.line_ids:
                    if line.attribute_line_id.attribute_id.type_rolls == 'model':
                        line.product_template_attribute_value_filter = record.product_template_attribute_value_id.id or None
                        #raise ValueError([line.product_template_attribute_value_filter,record.product_template_attribute_value_id])



'''





