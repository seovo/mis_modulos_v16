
from odoo import models, exceptions, fields , api , _

class SaleOrder(models.Model):
    _inherit = "purchase.order.line"
    serie_jz = fields.Char(string="Serie")
    numeral_jz = fields.Char(string="Numero")

    @api.onchange('serie_jz','numeral_jz')
    def change_serie_numeral_jz(self):
        for record in self:
            if record.serie_jz and record.numeral_jz:
                record.partner_ref = f'{record.serie_jz}-{record.numeral_jz}'


    @api.onchange('name')
    def change_name_jz(self):
        for record in self:
            if not record.product_id:
                product = self.env['product.product'].search([('is_product_purchase','=',True)],limit=1)
                if product:
                    record.product_id = product.id



class SaleOrder(models.Model):
    _inherit = "sale.order"
    purchase_order_line_ids = fields.One2many('purchase.order.line','sale_id')
    purchase_ids            = fields.Many2many('purchase.order',compute='get_purchase_ids')
    total_purchase          = fields.Float(string="Total Compra",compute='get_purchase_ids')
    neto_amount_total       = fields.Float(string="Neto Monto",compute='get_purchase_ids')

    @api.depends('purchase_order_line_ids','purchase_order_line_ids.price_total')
    def get_purchase_ids(self):
        for record in self:
            purchase_ids = []
            total = 0
            for line in record.purchase_order_line_ids:
                if  line.order_id.id  not in purchase_ids:
                    purchase_ids.append(line.order_id.id)
                total += line.price_total
            record.purchase_ids = [(6,0,purchase_ids)] if purchase_ids else None
            record.total_purchase  = total
            record.neto_amount_total = record.amount_total - total


