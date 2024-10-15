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
    ],string="Clase de Encomienda",required=True)

    type_doc_encomienda  = fields.Selection([
        ('doc','Documento'),
        ('mer','Mercaderia'),
    ],string="Clase de Documentos",required=True)
    packing_list_ids = fields.One2many('sale.order.packing.list','order_id')

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
    qty = fields.Float(string="Cantidad")
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
    ],required=True)
    name = fields.Text(string="Descripción")
    code_hds = fields.Char(string="Codigo HDS")

