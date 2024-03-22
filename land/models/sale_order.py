from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def write(self,values):
        res = super().write(values)
        return res
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line( **optional_values)
        if self.product_id.payment_land_dues:
            res['quantity'] = 1
        return res

    def create(self,values):
        res = super().create(values)
        for record in res:

            for line in record.order_id.order_line:
                line.change_product_uom_qty_land()

        return res

    def _price_land(self,product,returnx=False,qty=None,inicial=0):
        price_total = 1
        is_land = False
        if product.product_template_attribute_value_ids:

            price_totalx = 1
            # array_total = []
            for value_line in product.product_template_attribute_value_ids:
                value = value_line.product_attribute_value_id
                if value.type_land:
                    is_land = True
                    price_totalx = price_totalx * value.value_land
                    # array_total.append(value.value_land)
            # raise ValueError([array_total,price_total , record.product_uom_qty,price_total / record.product_uom_qty])
            if is_land:
                price_total = price_totalx
                if not returnx:
                    self.price_unit = ( price_totalx - inicial ) / self.product_uom_qty

        if returnx and is_land:
            if qty:
                price_total = price_total / qty
            return price_total


    @api.onchange('product_uom_qty','product_id','price_unit')
    def change_product_uom_qty_land(self,check=True):
        #raise ValueError(self.order_id.order_line)
        for record in self:
            inicial = 0
            for line in record.order_id.order_line:
                #raise ValueError([line.product_template_id,record.product_template_id.optional_product_ids.ids])
                if line.product_template_id.id in  record.product_template_id.optional_product_ids.ids:
                    inicial = line.product_template_id.list_price
                    #raise ValueError(inicial)

            record._price_land(record.product_id,inicial = inicial)
            if check:
                for line in record.order_id.order_line:
                    line.change_product_uom_qty_land(check=False)





