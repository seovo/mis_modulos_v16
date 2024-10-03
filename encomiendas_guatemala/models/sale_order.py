from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit       = 'sale.order'
    state_encomienda = fields.Selection([
        ('1','Transito Caja Rural al Cenam'),
        ('2','Despacho a USA'),
        ('3', 'Salio a Aduana'),
        ('4', 'Entregado'),
    ])