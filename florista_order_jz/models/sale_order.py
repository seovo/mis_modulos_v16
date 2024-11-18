from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    date_shipment_florista = fields.Date(string='Fecha Envio Flores')
    number_period_florista = fields.Integer(string="Nro Periodo", compute="get_data_florista",store=True)
    interval_period_florista = fields.Integer(string="Dias Intervalo", compute="get_data_florista",store=True)


    @api.depends('order_line','order_line.product_id')
    def get_data_florista(self):
        for record in self:
            record.number_period_florista = None
            record.interval_period_florista = None

            for line in record.order_line:
                if line.product_id:
                    for value in  line.product_id.product_template_attribute_value_ids:
                        if value.attribute_id.is_period_florista:
                            record.number_period_florista = value.product_attribute_value_id.number_period_florista
                            record.interval_period_florista = value.product_attribute_value_id.interval_period_florista




