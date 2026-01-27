from odoo import models, fields , api
from datetime import date , datetime , timedelta

class IntermedioCD(models.Model):
    _name = 'datawave.intermedio.cd'
    _description = 'IntermedioCD de Datawave'

    date = fields.Date(string='Fecha', required=True)
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    cd_id = fields.Many2one('datawave.cd', string='CD')
    seller_id = fields.Many2one('datawave.seller',string='Proveedor')
    lt_days      = fields.Integer(string='LT Dias')
    forecast_day = fields.Integer(string='Forecast Diario')
    sigma        = fields.Float(string='Sigma')
    moq          = fields.Float(string='Moq')
    stock        = fields.Integer(string='Stock')
    stock_transit = fields.Integer(string='Stock Transito')
    stock_forecast = fields.Integer(string='Stock Pronosticado')
    ss = fields.Float(string='SS', help='Z*Sigma*SQRT(LT)')
    freq = fields.Float(string='FREQ')
    max = fields.Float(string='MAX', help='(LT+FREQ)*Forecast+SS')
    rop = fields.Float(string='ROP', help='Forecast*LT+SS')
    quantity = fields.Integer(string='Cantidad Sugerida', help='MAX(0,MAX-Stock)')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')
    datawave_sale_ids = fields.Many2many('datawave.sale.cd', string='Ventas')


    def set_historico_sigma(self):

        record = self


        sigma_dias = self.env['ir.config_parameter'].sudo().get_param('datawave.ventana_sigma_dias_cd')
        sigma_dias = int(sigma_dias) if sigma_dias else 0

        today = record.date
        limit_date = today - timedelta(days=sigma_dias)

        # DIAS LOBORALES

        domain = [
            ('product_id', '=', record.product_id.id), ('cd_id', '=', record.cd_id.id),
            ("date", ">=", limit_date), ("date", "<", today),
        ]

        historico = self.env['datawave.sale.cd'].search(domain)
        # raise ValueError(historico)
        if historico:

            record.datawave_sale_ids = [(6, 0, historico.ids)]

            import statistics
            datos = []
            for hist in historico:
                datos.append(hist.quantity)
            # raise ValueError(datos)
            desviacion_estandar_poblacional = statistics.pstdev(datos)
            # raise ValueError(desviacion_estandar_poblacional)
            record.sigma = desviacion_estandar_poblacional
        else:
            record.datawave_sale_ids = False
        #    raise ValueError(domain)


    @api.onchange('product_id', 'cd_id', 'date','seller_id')
    def change_product_tienda(self):
        for record in self:
            record.lt_days = 0



            if not record.product_id or not record.cd_id  or not record.date or not record.seller_id:
                continue

            config_tienda_p = self.env['datawave.config.proveedor.cd'].search([
                ('product_id', '=', record.product_id.id), ('seller_id', '=', record.seller_id.id),
                ('cd_id','=',record.cd_id.id)
            ])

            #raise ValueError(config_tienda_p)

            record.lt_days = config_tienda_p.lt_days if config_tienda_p else 0


            forecast_day = self.env['datawave.forecast.cd'].search([
                ('product_id', '=', record.product_id.id), ('cd_id', '=', record.cd_id.id)
            ])

            record.forecast_day = forecast_day.forecast_day

