from odoo import _, api, fields, models



class ProductProductFlorista(models.Model):
    _name = 'product.product.florista'
    _order = 'sequence'
    sequence = fields.Integer()
    product_attribute_value_id = fields.Many2one('product.attribute.value')
    product_terminado_id = fields.Many2one('product.product',string="Producto Terminado")



class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    is_period_florista = fields.Boolean(string='Es Periodo Flores')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    is_period_florista = fields.Boolean(related='attribute_id.is_period_florista')
    number_period_florista = fields.Integer(string="Nro Periodo")
    interval_period_florista = fields.Integer(string="Dias Intervalo")
    product_florista_ids = fields.One2many('product.product.florista', 'product_attribute_value_id')

    image = fields.Image(
        string="Imagen",
        help="You can upload an image that will be used as the color of the attribute value.",
        max_width=2250,
        max_height=2250,
    )

    def edit_products(self):
        view = self.env.ref('florista_order_jz.edit_product_atrv')
        return {
            "name": f"EDIT PRODUCTS :   {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.attribute.value",
            "target": "new",
            "res_id": self.id,
            "view_id": view.id
        }