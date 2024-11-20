from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')
    number_period_florista = fields.Integer(string="Nro Periodo", compute="get_data_florista",store=True)
    interval_period_florista = fields.Integer(string="Dias Intervalo", compute="get_data_florista",store=True)
    product_terminado_florista = fields.Many2one('product.product', compute="get_data_florista")
    next_order_number_list = fields.Integer(string="Siguiente # de Producto Terminado")


    @api.depends('order_line','order_line.product_id')
    def get_data_florista(self):
        for record in self:
            record.number_period_florista = None
            record.interval_period_florista = None
            record.product_terminado_florista = None

            for line in record.order_line:
                if line.product_id:
                    for value in  line.product_id.product_template_attribute_value_ids:
                        if value.attribute_id.is_period_florista:
                            record.number_period_florista = value.product_attribute_value_id.number_period_florista
                            record.interval_period_florista = value.product_attribute_value_id.interval_period_florista
                            record.product_terminado_florista = line.product_id.id


    def add_envio_florista(self,c=0):

        #raise ValueError(self.product_terminado_florista)
        if self.product_terminado_florista:
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



                        for product_f in value.product_attribute_value_id.product_florista_ids:

                            if ct >= c :
                                #c += 1

                                # raise ValueError([c,self.number_period_florista])

                                # if c > len(value.product_attribute_value_id.product_florista_ids)  :
                                if ctt > self.number_period_florista:
                                    raise ValueError([ctt,self.number_period_florista])
                                    break
                                self.order_line += self.env['sale.order.line'].new({
                                    'product_id': product_f.product_terminado_id.id,
                                    'name': product_f.product_terminado_id.display_name,
                                    'product_uom_qty': 1,
                                    'price_unit': 0,
                                    'tax_id': None
                                })
                                ctt += 1

                            ct += 1







