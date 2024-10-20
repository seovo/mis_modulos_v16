from email.policy import default

from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit       = 'sale.order'
    state_encomienda = fields.Selection([
        ('1','Transito Caja Rural al Cenam'),
        ('2','Despacho a USA'),
        ('3', 'Salio a Aduana'),
        ('4', 'Entregado'),
    ],default='1',string="Estado Encomienda")

    clase_encomienda  = fields.Selection([
        ('doc','Documento'),
        ('mer','Mercaderia'),
    ],string="Clase de Encomienda")

    type_doc_encomienda  = fields.Selection([
        ('doc','Legales'),
        ('pass','Pasaporte'),
        ('lic','Licencia'),
        ('other','Otro')
    ],string="Clase de Documentos")
    packing_list_ids = fields.One2many('sale.order.packing.list','order_id')

    def action_confirm(self):
        res = super().action_confirm()
        if self.carrier_id:
            for line in self.order_line:
                carrier = self.carrier_id
                if line.product_id == self.carrier_id.product_id:
                    line.unlink()
                self.carrier_id = carrier.id

        return res

    #PACKING LIST

class SaleOrderPackingList(models.Model):
    _name = "sale.order.packing.list"
    _description = "sale.order.packing.list"

    order_id = fields.Many2one('sale.order')
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    sequence = fields.Integer(string="Sequence", default=10)
    qty = fields.Float(string="Cantidad",default=1)
    type_mercaderia = fields.Selection([
        ('food_refrigeration','Comida que requiere refrigeración'),
        ('sweet', 'Dulces típicos'),
        ('broth', 'Caldo'),
        ('food_registration', 'Comida con registros ejemplo tortrix o boquitas Diana'),
        ('beer','Cerveza'),
        ('medicines', 'Medicinas'),
        ('creams', 'Cremas'),
        ('clothes', 'Ropa'),
        ('other', 'Otros Especificar :'),
    ],required=True,string="Mercaderia")
    name = fields.Text(string="Descripción")
    code_hds = fields.Char(string="Codigo HDS")


class SaleOrderLine(models.Model):
    _inherit        = 'sale.order.line'
    encomienda_list = fields.One2many('sale.order.line.encomienda.list','sale_order_line_id')
    is_encomienda   = fields.Boolean(related='product_id.is_encomienda')
    price_fixed     = fields.Float(compute='change_items_encomienda',string='Precio Fijo')
    price_total_encomienda =  fields.Float(compute='change_items_encomienda',string='Precio Total Encomienda')
    cost_price_cobro = fields.Float(compute='change_items_encomienda', string='Costo Precio Cobro')

    @api.onchange('encomienda_list','encomienda_list.amount_total')
    def change_items_encomienda(self):
        for record in self:
            if record.product_id:

                total_peso_cobro = 0
                total_price = 0

                for line in record.encomienda_list:
                    total_peso_cobro  += line.weight_cobrar
                    total_price +=  line.amount_total

                if total_peso_cobro > 0 :
                    total_peso_cobro = total_peso_cobro - 1
                    total_peso_cobro = total_peso_cobro * record.product_id.price_extra_libre

                record.cost_price_cobro = total_peso_cobro

                record.price_total_encomienda = total_price
                record.price_fixed = record.product_id.list_price
                record.price_unit = record.price_fixed + total_peso_cobro + total_price


    def edit_price_jz(self):

        if not self.is_encomienda:
            return

        view = self.env.ref('encomiendas_guatemala.edit_sale_order_line')
        return {
            "name": f"EDIT PRICE :   {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "target": "new",
            "res_id": self.id ,
            "view_id": view.id
        }


class SaleOrderEncomiendaList(models.Model):
    _name = "sale.order.line.encomienda.list"
    _description = "sale.order.encomienda.list"

    sale_order_line_id = fields.Many2one('sale.order.line')
    qty = fields.Float(string="Cantidad",default=1)
    product_id = fields.Many2one('product.product',string="Producto",required=True)
    price_unit = fields.Float(string="Precio")
    precio_cost = fields.Float(string="Costo")
    peso_real   = fields.Float(string="Peso Real (lb)")
    largo       = fields.Float(string="Largo (cm)")
    ancho       = fields.Float(string="Ancho (cm)")
    alto        = fields.Float(string="Alto (cm)")
    weight_vol  = fields.Float(string="Peso Volumen",compute='get_weight_vol')
    weight_cobrar = fields.Float(string="Peso Cobro",compute='get_weight_vol')
    amount_total = fields.Float(string="Total",compute="get_amount_total")

    @api.depends('price_unit','qty')
    def get_amount_total(self):
        for record in self:
            record.amount_total = record.price_unit * record.qty


    @api.depends('peso_real','largo','ancho','alto')
    def get_weight_vol(self):
        for record in self:

            mult =  ( record.largo * record.ancho * record.alto ) / 5000

            record.weight_vol = round(mult * 2.2046,0)

            record.weight_cobrar = max(record.weight_vol,record.peso_real)

    @api.onchange('product_id')
    def change_product(self):
        for record in self:
            record.price_unit = record.product_id.list_price
            record.precio_cost = record.product_id.standard_price






