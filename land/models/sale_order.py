from odoo import api, fields, models , _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nro_internal_land =  fields.Char()
    mz_lot            =  fields.Char()
    sector  =  fields.Char()
    stage_land = fields.Selection([
        ('signed',_('Signed'))
    ])

    m2_land = fields.Char()
    dues_land = fields.Float()
    value_due_land = fields.Float()
    crono_land = fields.Char()
    days_tolerance_land  = fields.Integer()
    value_mora_land = fields.Float()
    percentage_refund_land = fields.Float()

    date_sign_land = fields.Date()
    date_first_due_land = fields.Date()

    modality_land = fields.Selection([
        ('single',_('Single')) ,
        ('low_customer',_('Low Customer')) ,
        ('married',_('Married')) ,
        ('divorcee',_('Divorcee')) ,
        ('confirmer',_('Confirmer')) ,
        ('widow',_('Widow')) ,
        ('transfer',_('Transfer')) ,
    ])

    obs_modality_land = fields.Text()
    price_total_land = fields.Float()
    price_initial_land = fields.Float()
    price_credit_land = fields.Float()




    def _recalcule_price_land(self):
        for record in self:

            for line in record.order_line:
                if line.product_id and line.product_id.payment_land_dues:

                    line.change_product_uom_qty_land()


    def write(self,values):
        res = super().write(values)
        return res
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def edit_price_jz(self):
        view = self.env.ref('land.edit_sale_order_line')
        return {
            "name": f"EDIT PRICE :   {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "target": "new",
            "res_id": self.id ,
            "view_id": view.id
        }

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
                if value.type_land and value.type_land in ['stage','m2']:
                    is_land = True
                    price_totalx = price_totalx * value.value_land
                    # array_total.append(value.value_land)
            # raise ValueError([array_total,price_total , record.product_uom_qty,price_total / record.product_uom_qty])
            if is_land:
                price_total = price_totalx
                if not returnx:
                    price_final = ( price_totalx - inicial ) / self.product_uom_qty
                    #raise ValueError([self.name,price_final,price_totalx, inicial])
                    self.price_unit = price_final

        if returnx and is_land:
            if qty:
                price_total = price_total / qty
            return price_total


    def _calculate_price_land(self):
        for record in self:
            inicial = 0
            for line in record.order_id.order_line:
                # raise ValueError([line.product_template_id,record.product_template_id.optional_product_ids.ids])
                if line.product_template_id.id in record.product_template_id.optional_product_ids.ids:
                    inicial = line.price_unit
                    # raise ValueError(inicial)

            record._price_land(record.product_id, inicial=inicial)



    @api.onchange('product_uom_qty',)
    def change_product_uom_qty_land(self):
        for record in self:
            if record.product_id and record.product_id.is_advanced_land:
                record.product_uom_qty = 1
            record._calculate_price_land()

    @api.onchange('product_id')
    def change_product_id_land(self):
        #raise ValueError(self.order_id.order_line)
        for record in self:

            if  record.product_id and record.product_id.payment_land_dues:
                record.product_uom_qty = record.product_id.dues_qty

            if  record.product_id and record.product_id.is_advanced_land:
                record.product_uom_qty = 1

            record._calculate_price_land()


    def write(self,values):
        res = super().write(values)
        for record in self:
            if record.product_id and record.product_id.is_advanced_land:
                record.order_id._recalcule_price_land()
        return res







