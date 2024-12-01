from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class UntilHourFlorista(models.Model):
    _name = 'until.hour.florista'
    _order = 'sequence'
    name = fields.Char(required=True)
    value = fields.Float()
    sequence = fields.Integer()

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')
    until_hour_florista = fields.Many2one('until.hour.florista',string="Entregar Hasta")

    number_period_florista = fields.Integer(string="Nro Periodo", compute="get_data_florista",store=True)
    interval_period_florista = fields.Integer(string="Dias Intervalo", compute="get_data_florista",store=True)
    product_terminado_florista = fields.Many2one('product.product', compute="get_data_florista")
    next_order_number_list = fields.Integer(string="Siguiente # de Producto Terminado")
    product_attribute_value_florista_id = fields.Many2one('product.attribute.value', compute="get_data_florista")


    @api.depends('order_line','order_line.product_id')
    def get_data_florista(self):
        for record in self:
            record.number_period_florista = None
            record.interval_period_florista = None
            record.product_terminado_florista = None
            record.product_attribute_value_florista_id = None

            for line in record.order_line:
                if line.product_id:
                    for value in  line.product_id.product_template_attribute_value_ids:
                        if value.attribute_id.is_period_florista:
                            record.number_period_florista = value.product_attribute_value_id.number_period_florista
                            record.interval_period_florista = value.product_attribute_value_id.interval_period_florista
                            record.product_terminado_florista = line.product_id.id
                        if value.product_attribute_value_id.product_florista_ids:
                            record.product_attribute_value_florista_id = value.product_attribute_value_id.id



    def add_envio_florista(self,c=0):

        #raise ValueError(self.product_terminado_florista)
        if self.product_terminado_florista and self.id_vex:
            suscripcion = None
            for line in self.order_line:
                if line.price_unit != 0:
                    suscripcion = line.product_id

            if suscripcion:
                for value in suscripcion.product_template_attribute_value_ids:
                    if value.product_attribute_value_id.product_florista_ids:


                        ct = 0
                        ctt = 0

                        len_p = len(value.product_attribute_value_id.product_florista_ids)

                        if c > len_p:
                            c = 0

                        florista_ids = value.product_attribute_value_id.product_florista_ids

                        array_florista = []

                        for fl in florista_ids:
                            array_florista.append(fl.id)


                        for product_f in  florista_ids + florista_ids + florista_ids:

                            if ct >= c :

                                if ctt >= self.number_period_florista:
                                    #raise ValueError([ctt,self.number_period_florista])
                                    break
                                self.order_line += self.env['sale.order.line'].new({
                                    'product_id': product_f.product_terminado_id.id,
                                    'name': product_f.product_terminado_id.display_name,
                                    'product_uom_qty': 1,
                                    'price_unit': 0,
                                    'tax_id': None
                                })
                                self.next_order_number_list = array_florista.index(product_f.id) + 1 + 1
                                ctt += 1

                            ct += 1



    def action_confirm(self):
        res = super().action_confirm()

        if not self.product_terminado_florista:
            return

        if not self.date_shipment_florista:
            raise ValidationError('Indique 1ra Fecha Envio')

        if not self.until_hour_florista:
            raise ValidationError('Indique un valor para el campo "Entregar Hasta"')

        picking = self.picking_ids[0]
        picking_news = []

        if picking and self.number_period_florista > 1:
            for i in range(self.number_period_florista - 1):
                new = picking.copy()
                picking_news.append(new)

        total_pickings = [picking] + picking_news

        c = 0


        date_envio = self.date_shipment_florista

        for line in self.order_line:

            if line.product_id and self.product_terminado_florista != line.product_id:

                if c > 0 :
                    date_envio = date_envio + timedelta(days=self.interval_period_florista)

                pickii = total_pickings[c]
                pickii.scheduled_date = date_envio
                pickii.scheduled_date = pickii.scheduled_date + timedelta(hours=5) + timedelta(hours=self.until_hour_florista.value)
                for move in pickii.move_ids_without_package:
                    if move.product_id != line.product_id:
                        move.unlink()





                c += 1

        c = 0

        for line in self.order_line and 5 == 7:
            if line.product_id and self.product_terminado_florista != line.product_id:
                pickii = total_pickings[c]
                for move in pickii.move_ids_without_package:
                    if self.product_attribute_value_florista_id.products_fixed:
                        for pfixed in self.product_attribute_value_florista_id.products_fixed:
                            line.product_uom_qty += 1
                            move.copy(default={'product_id': pfixed.id})
                    if self.product_attribute_value_florista_id.product_first_order and self.shipping_vex == 1:
                        for pfirst in self.product_attribute_value_florista_id.product_first_order:
                            line.product_uom_qty += 1
                            move.copy(default={'product_id': pfirst.id})
                c += 1


        return res