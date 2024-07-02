from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

meses_espanol = {
    1: 'enero',
    2: 'febrero',
    3: 'marzo',
    4: 'abril',
    5: 'mayo',
    6: 'junio',
    7: 'julio',
    8: 'agosto',
    9: 'septiembre',
    10: 'octubre',
    11: 'noviembre',
    12: 'diciembre'
}


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


    def get_descript_next_due(self,sale_line):
        fecha_actual = self.order_id.next_payment_date_land or fields.Datetime.now()
        # mes = fecha_actual.strftime('%B')  # El mes completo en español
        anio = fecha_actual.year

        # Obtener el número del mes
        mes_actual = fecha_actual.month

        # Obtener el nombre del mes en español
        mes_actual_espanol = meses_espanol[mes_actual]

        mes_ano = f' , {mes_actual_espanol} - {anio}'

        if self.product_id.manzana and self.product_id.lote:
            name = f"CANCELACION  CUOTA  {int(sale_line.qty_invoiced + 1)} , MZ: {self.product_id.manzana} - LT : {self.product_id.lote} {mes_ano} "
            return name
        else:
            if sale_line.order_id.mz_lot:
                name = f"CANCELACION  CUOTA {int(sale_line.qty_invoiced + 1)} , {sale_line.order_id.mz_lot} {mes_ano}"
                return name

        if self.product_id.is_advanced_land:

            if self.product_id.manzana and self.product_id.lote:
                return f"CANCELACION  INICIAL  , MZ: {self.product_id.manzana} - LT : {self.product_id.lote} "
            else:

                return f"CANCELACION  INICIAL ,  {sale_line.order_id.mz_lot or ''} "


    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line( **optional_values)
        if self.product_id.payment_land_dues:
            res['quantity'] = 1

        if self.order_id.price_unit_import and self.order_id.price_unit_import != 0:
            res['price_unit'] = self.order_id.price_unit_import

        sale_line = self.env['sale.order.line'].browse(res['sale_line_ids'][0][1])

        name = self.get_descript_next_due(sale_line)
        if name:
            res['name'] = name


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
                if line.product_template_id.is_advanced_land:
                    inicial += line.price_unit
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



    def create(self,values):
        res = super().create(values)
        for record in res:

            if record.product_id:
                mz_lot = f'{record.product_id.manzana}-{record.product_id.lote}'

                exist = self.env['sale.order'].search(
                    [('company_id', '=', record.company_id.id), ('mz_lot', '=', mz_lot), ('id', '!=', record.order_id.id),
                     ('state', 'in', ['done', 'sale']),('stage_land','!=','cancel')])

                if exist:
                    raise ValidationError(f'NO PUEDE HABER MANZANA Y LOTE REPETIDOS ')






            for line in record.order_id.order_line:
                line.change_product_uom_qty_land()

        return res