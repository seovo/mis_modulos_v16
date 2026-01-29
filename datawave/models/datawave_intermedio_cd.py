from odoo import models, fields , api
from datetime import date , datetime , timedelta

class IntermedioCD(models.Model):
    _name = 'datawave.intermedio.cd'
    _description = 'IntermedioCD de Datawave'

    date = fields.Date(string='Fecha', required=True)
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    product_description = fields.Char(string='Descripción', related='product_id.description')
    product_state = fields.Char(string='Estado', related='product_id.state')
    cd_id = fields.Many2one('datawave.cd', string='CD')
    seller_id = fields.Many2one('datawave.seller',string='Proveedor',required=True)
    lt_days      = fields.Integer(string='LT Dias')
    forecast_day = fields.Integer(string='Forecast Diario')
    sigma        = fields.Float(string='Sigma')
    moq          = fields.Float(string='Moq')
    stock        = fields.Integer(string='Stock')
    stock_transit = fields.Integer(string='Stock Transito')
    stock_forecast = fields.Integer(string='Stock Pronosticado')
    stock_forecast_day = fields.Integer(string='Stock Pronosticado Dias')
    ss = fields.Float(string='SS', help='Z*Sigma*SQRT(LT)')
    freq = fields.Float(string='FREQ')
    max = fields.Float(string='MAX', help='(LT+FREQ)*Forecast+SS')
    rop = fields.Float(string='ROP', help='Forecast*LT+SS')
    quantity = fields.Integer(string='Cantidad Sugerida', help='MAX(0,MAX-Stock)')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')
    datawave_sale_ids = fields.Many2many('datawave.sale.cd', string='Ventas')
    riesgo = fields.Selection([
        ('0', 'Sin Riesgo'), ('1', 'Riesgo 1'), ('2', 'Riesgo 2'), ('3', 'Riesgo 3')
    ])
    sobreestock = fields.Selection([
        ('0', 'Sin SobreStock'), ('1', 'SobreStocko 1'), ('2', 'SobreStock 2')
    ])


    def set_historico_sigma(self,sigma_dias):

        record = self


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

    def set_moq(self,config_tienda_p):
        moq = config_tienda_p.moq

        if moq > 0 :
            self.moq = moq
        else:
            self.moq = self.seller_id.moq_default


    def set_stock_seguridad(self,conf_ss):

        if conf_ss == 1:
            import math

            # Calcular la raíz cuadrada
            raiz_cuadrada = math.sqrt(self.lt_days)
            self.ss = conf_ss * self.sigma * raiz_cuadrada
        else:
            self.ss = self.lt_days * self.forecast_day

    def set_stock_riesgo_sobrestock(self,stock_tienda):
        stock = 0



        if stock_tienda:
            stock = stock_tienda.stock

        self.stock = stock


        if self.stock <= 0:
            self.riesgo = '3'

        if self.stock > 0 and self.stock < self.ss:
            self.riesgo = '2'

        if self.stock >= self.ss and self.stock < self.rop:
            self.riesgo = '1'
        if self.stock >= self.ss and self.stock >=  self.rop :
            self.riesgo = '0'


        ###SOBRE STOCK
        if self.stock > self.max + self.ss :
            self.sobreestock = '2'
        else:
            if self.stock > self.max :
                self.sobreestock = '1'
            else:
                self.sobreestock = '0'

        ##

        domain = [
            ('cd_id', '=', self.cd_id.id),
            ('product_id', '=', self.product_id.id)
        ]

        stock_resume = self.env['datawave.transit.cd.resume'].search(domain)

        self.stock_transit = stock_resume.stock if stock_resume else 0
        self.stock_forecast = self.stock + self.stock_transit
        self.stock_forecast_day = self.stock_forecast / self.forecast_day if self.forecast_day != 0 else 0

        #self.quantity = max(self.stock, self.max)


    def set_frecuency(self,conf_frecuencia,config_tienda):
        #,forecast_tienda_day
        conf = conf_frecuencia
        if not config_tienda:
            return

        #frecuencia fija
        if conf == 1 :
            self.freq = config_tienda.frecuency_empirical

        if conf == 2:
            if config_tienda.cost_keep  != 0:
                #EOQ
                base_raiz = (2 * self.forecast_day * 365 * config_tienda.cost_sale) / config_tienda.cost_keep
                self.freq = math.sqrt(base_raiz)
            else:
                self.freq = 0

        if conf == 3:
            self.freq = config_tienda.days_target

        if conf == 4:
            self.freq = self.lt_days + config_tienda.days_delta

        if conf == 5:
            self.freq = self.forecast_day / self.moq if self.moq else 0

    def set_max(self):
        self.max = 0

        conf = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_max_cd')
        conf = int(conf) if conf else 0

        if conf == 1 :
            self.max = ( 2 * self.forecast_day * self.lt_days ) + (self.forecast_day + self.freq)


        if conf == 2:
            self.max = (self.lt_days * self.freq ) + self.ss


    def set_sugerido_redondeo(self,config_tienda_p):
        condicion = self.quantity

        if condicion <= 0 :
            self.quantity_round = 0

        else:
            if condicion <= self.moq :
                self.quantity_round = self.moq
            else:
                def multiplo_superior(numero, constante):
                    if constante <= 0:
                        raise ValueError("La constante debe ser mayor que 0.")
                    return ((numero + constante - 1) // constante) * constante

                resultado = multiplo_superior(self.quantity, config_tienda_p.round_cd)
                self.quantity_round = resultado




    @api.onchange('product_id', 'cd_id', 'date','seller_id')
    def change_product_tienda(self):

        sigma_dias = self.env['ir.config_parameter'].sudo().get_param('datawave.ventana_sigma_dias_cd')
        sigma_dias = int(sigma_dias) if sigma_dias else 0

        conf_ss = self.env['ir.config_parameter'].sudo().get_param('datawave.z_cd')
        conf_ss = float(conf_ss) if conf_ss else 0

        conf_frecuencia = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_frecuencia_cd')
        conf_frecuencia = int(conf_frecuencia) if conf_frecuencia else 0



        for record in self:
            record.lt_days = 0
            record.datawave_sale_ids = False
            record.sigma = 0
            record.forecast_day = 0
            record.moq = 0
            record.ss = 0
            record.stock = 0
            record.sobreestock = 0
            record.riesgo = 0
            record.stock_transit = 0
            record.stock_forecast = 0
            record.stock_forecast_day = 0
            record.freq = 0



            if not record.product_id or not record.cd_id  or not record.date or not record.seller_id:
                continue

            config_tienda_p = self.env['datawave.config.proveedor.cd'].search([
                ('product_id', '=', record.product_id.id), ('seller_id', '=', record.seller_id.id),
                ('cd_id','=',record.cd_id.id)
            ])

            forecast_day = self.env['datawave.forecast.cd'].search([
                ('product_id', '=', record.product_id.id), ('cd_id', '=', record.cd_id.id)
            ])

            domain = [
                ('cd_id', '=', record.cd_id.id),
                ('product_id', '=', record.product_id.id),
                ('date', '=', record.date)
            ]
            stock_tienda = self.env['datawave.stock.cd'].search(domain)

            record.lt_days = config_tienda_p.lt_days if config_tienda_p else 0
            record.forecast_day = forecast_day.forecast_day if forecast_day else 0


            record.set_historico_sigma(sigma_dias)
            record.set_moq(config_tienda_p)
            record.set_stock_riesgo_sobrestock(stock_tienda)
            record.set_stock_seguridad(conf_ss)
            record.set_frecuency(conf_frecuencia,config_tienda_p)
            record.set_max()

            record.rop = record.forecast_day + record.lt_days + record.ss
            record.quantity = max(0,self.max-self.stock_forecast)
            record.set_sugerido_redondeo(config_tienda_p)






