from odoo import models, exceptions, fields , _

class PaymentSaleOrder(models.Model):
    _name = "payment.sale.order"
    _description = "payment.sale.order"
    sale_id = fields.Many2one('sale.order')
    amount = fields.Float(string="Monto Pagado")
    date = fields.Date(string="Fecha")
    note = fields.Text(string="Notas")