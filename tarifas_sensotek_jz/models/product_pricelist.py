from odoo import api, fields, models

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    is_escale_sonsotec = fields.Boolean(string="Es una Escala")
    amount_escale_sonsote = fields.Float(string='Monto Escala')
    use_discount_category_sonsotec =  fields.Boolean(string="Usar Descuento de Categoria")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def change_escale_proce(self):
        for record in self:
            tarifa = self #definir  la tarifa
            if tarifa.is_escale_sonsotec:
                price_unit = record.list_price or record.acquisition_cost

                price_unitx = price_unit - (price_unit * record.categ_id.supplier_disc / 100)

                price_unitx = price_unitx / tarifa.amount_escale_sonsote if tarifa.amount_escale_sonsote != 0 else  0

                record.price_unit = price_unit



