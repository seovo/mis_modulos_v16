from email.policy import default

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

    add_separation_land = fields.Float(string="Agregar Separación")
    amount_initial_desc = fields.Float()

    land_area_id  = fields.Many2one('product.template.attribute.value', string="Area")
    land_mz_id    = fields.Many2one('product.template.attribute.value', string="Manzana")
    land_lote_id  = fields.Many2one('product.template.attribute.value', string="Lote")
    land_stage_id = fields.Many2one('product.template.attribute.value', string="Etapa")

    is_create_of_origin_idenpencia = fields.Boolean(default=True)




    def edit_price_jz(self):
        self.add_separation_land = 0
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


        if self.product_id.is_anticipo_land:

            if self.product_id.manzana and self.product_id.lote:
                return f"ANTICIPO  , MZ: {self.product_id.manzana} - LT : {self.product_id.lote} "
            else:

                return f"ANTICIPO ,  {sale_line.order_id.mz_lot or ''} "

        if self.product_id.is_separation_land:

            if self.product_id.manzana and self.product_id.lote:
                return f"SEPARACION  , MZ: {self.product_id.manzana} - LT : {self.product_id.lote}  {self.product_id.description_sale}"
            else:

                return f"SEPARACION ,  {sale_line.order_id.mz_lot or ''}  {self.product_id.description_sale}"




        if self.product_id.is_advanced_land:

            if self.product_id.manzana and self.product_id.lote:
                return f"CANCELACION  INICIAL  , MZ: {self.product_id.manzana} - LT : {self.product_id.lote} {self.product_id.description_sale}"
            else:

                return f"CANCELACION  INICIAL ,  {sale_line.order_id.mz_lot or ''}  {self.product_id.description_sale}"


        if self.product_id.manzana and self.product_id.lote:
            name = f"CANCELACION  CUOTA  {int(sale_line.order_id.qty_dues_payment + 1)} , MZ: {self.product_id.manzana} - LT : {self.product_id.lote} {mes_ano} "
            return name
        else:
            if sale_line.order_id.mz_lot:
                name = f"CANCELACION  CUOTA {int(sale_line.order_id.qty_dues_payment + 1)} , {sale_line.order_id.mz_lot} {mes_ano}"
                return name



    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line( **optional_values)
        if self.product_id.payment_land_dues or  self.product_id.is_advanced_land or self.product_id.is_independence:
            res['quantity'] = 1

        #if self.order_id.price_unit_import and self.order_id.price_unit_import != 0:
        #    res['price_unit'] = self.order_id.price_unit_import

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
                    inicial += line.price_total
                    # raise ValueError(inicial)

            record._price_land(record.product_id, inicial=inicial)



    @api.onchange('product_uom_qty',)
    def change_product_uom_qty_land(self):
        for record in self:
            #if record.product_id and record.product_id.is_advanced_land:
            #    record.product_uom_qty = 1
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


    def check_adelanto(self):
        for record in self:
            if record.move_separation_land_id:
                if len(record.order_line) == 2:
                    for line in record.order_line:
                        if line.product_id.is_advanced_land:
                            clone_line = line.copy(default={
                                'order_id': record.id ,
                                'product_id': record.move_separation_land_id.invoice_line_ids[0].product_id.id })
                            clone_line.price_unit = record.move_separation_land_id.amount_untaxed
                            line.price_unit = line.price_unit - clone_line.price_unit


    def write(self,values):
        #raise ValidationError(str(values))
        if 'land_area_id' in values or 'land_mz_id' in values or 'land_lote_id' in values or 'land_stage_id' in values:

            product_tmp   = values['product_template_id'] if  'product_template_id' in values else self.product_template_id.id
            land_area_id  = values['land_area_id']        if  'land_area_id'        in values else self.land_area_id.id
            land_mz_id    = values['land_mz_id']          if 'land_mz_id'           in values else self.land_mz_id.id
            land_lote_id  = values['land_lote_id']        if 'land_lote_id'         in values else self.land_lote_id.id
            land_stage_id = values['land_stage_id']       if 'land_stage_id'        in values else self.land_stage_id.id



            if product_tmp and land_area_id and land_mz_id and land_stage_id:
                product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', product_tmp),
                    ('product_template_attribute_value_ids.id', 'in', [land_area_id]),
                    ('product_template_attribute_value_ids.id', 'in', [land_mz_id]),
                    ('product_template_attribute_value_ids.id', 'in', [land_lote_id]),
                    ('product_template_attribute_value_ids.id', 'in', [land_stage_id]),

                ])

                if not product:
                    product = self.env['product.product'].sudo().create({
                        'product_tmpl_id': product_tmp,
                        'product_template_attribute_value_ids': [
                            (6, 0, [land_area_id, land_mz_id, land_lote_id , land_stage_id ])]
                    })

                values['product_id'] = product.id


                #raise ValidationError(str(product))



        res = super().write(values)
        for record in self:

            if record.add_separation_land and record.add_separation_land > 0 and record.product_id.is_advanced_land:

                if len(record.order_id.order_line) == 2:

                    dx = {
                        'name': 'Separación',
                        'order_id': record.order_id.id ,
                        'price_unit': record.add_separation_land
                        #"'product_id': record.move_separation_land_id.invoice_line_ids[
                        #                                0].product_id.id
                        }

                    product_separation =  self.env['product.product'].search([('is_separation_land','=',True)])

                    if product_separation:
                        dx.update({
                            'product_id': product_separation.id
                        })


                    clone_line = record.copy(default=dx)

                    clone_line.price_unit = record.add_separation_land
                    record.add_separation_land = 0

                    amount_initial_desc =  record.price_unit - clone_line.price_unit

                    record.price_unit = amount_initial_desc
                    record.amount_initial_desc = amount_initial_desc


                    #line.price_unit = line.price_unit - clone_line.price_unit

            if record.product_id and record.product_id.is_advanced_land:
                record.order_id._recalcule_price_land()

            record.verify_product_id()

            record.order_id.get_info_land()


        return res


    def verify_product_id(self):
        for record in self:
            if record.invoice_lines:
                for line in record.invoice_lines:

                    if line.product_id != record.product_id:
                        price_unit = line.price_unit
                        line.product_id = record.product_id.id
                        line.price_unit = price_unit
                    #line.price_unit = record.price_unit

    def create(self,values):
        res = super().create(values)
        for record in res:

            if record.product_id:
                mz_lot = f'{record.product_id.manzana}-{record.product_id.lote}'

                exist = self.env['sale.order'].search(
                    [('company_id', '=', record.company_id.id), ('mz_lot', '=', mz_lot), ('id', '!=', record.order_id.id),
                     ('state', 'in', ['done', 'sale']),('stage_land','!=','cancel')])

                if exist and not record.order_id.repeat_mz_lot:
                    raise ValidationError(f'{mz_lot} ya se encuentra separado o vendido')

                self.env['sale.order'].verifi_mz_lot(mz=record.product_id.manzana,lt=record.product_id.lote,object=record)




            for line in record.order_id.order_line:
                line.change_product_uom_qty_land()

            #buscar las demas ordenes

            if record.is_create_of_origin_idenpencia:
                orders = record.order_id.partner_id.sale_order_ids

                for orderr in orders:
                    if orderr != record.order_id:
                        if not orderr.price_independence_land or orderr.price_independence_land == 0:
                            record.copy(default={
                                'order_id': orderr.id ,
                                'is_create_of_origin_idenpencia' : False
                            })

        return res