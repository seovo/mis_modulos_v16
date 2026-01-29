from odoo import models, fields , api
from datetime import date , datetime , timedelta


class IntermedioTienda(models.Model):
    _name = 'datawave.intermedio.tienda'
    _description = 'IntermedioTienda de Datawave'
    #name         = fields.Char(string='Clave')
    date           = fields.Date(string='Fecha', required=True)
    product_id     = fields.Many2one('datawave.producto', string='Producto', required=True)
    product_description = fields.Char(string='Descripción', related='product_id.description')
    product_state  = fields.Char(string='Estado',related='product_id.state')
    tienda_id      = fields.Many2one('datawave.tienda', string='Tienda', required=True)
    lt_days        = fields.Integer(string='LT Dias')
    forecast_day   = fields.Float(string='Forecast Diario')
    sigma          = fields.Float(string='Sigma', digits=(16, 4))
    ss             = fields.Float(string='SS',help='Z*Sigma*SQRT(LT)')
    freq           = fields.Float(string='FREQ')
    max            = fields.Float(string='MAX',help='(LT+FREQ)*Forecast+SS')
    rop            = fields.Float(string='ROP',help='Forecast*LT+SS')
    stock          = fields.Integer(string='Stock')
    quantity       = fields.Integer(string='Cantidad Sugerida',help='MAX(0,MAX-Stock)')
    quantity_round     = fields.Integer(string='Cantidad Sugerida Redondeada')
    datawave_sale_ids  = fields.Many2many('datawave.sale',string='Ventas')
    forecast_tienda_id = fields.Many2one('datawave.forecast.tienda')
    riesgo             = fields.Selection([
        ('0','Sin Riesgo'),('1','Riesgo 1'),('2','Riesgo 2'),('3','Riesgo 3')
    ])
    sobreestock = fields.Selection([
        ('0', 'Sin SobreStock'), ('1', 'SobreStocko 1'), ('2', 'SobreStock 2')
    ])

    _sql_constraints = [
        (
            "unique_intermedio_tienda",
            "unique(date, product_id , tienda_id)",
            "NO PUEDE HABER REGISTROS DUPLICADOS",
        )
    ]

    #ESTABLECER EL FORECAST
    def set_forecast_day(self,forecast_tienda_day):
        record = self
        if forecast_tienda_day:
            record.forecast_tienda_id = forecast_tienda_day.id
            record.forecast_day = forecast_tienda_day.forecast_day
        else:
            record.forecast_tienda_id = None
            record.forecast_day = None

    def set_historico_sigma(self):

        record = self




        sigma_dias = self.env['ir.config_parameter'].sudo().get_param('datawave.ventana_sigma_dias')
        sigma_dias = int(sigma_dias) if sigma_dias else 0

        today = record.date
        limit_date = today - timedelta(days=sigma_dias)

        # DIAS LOBORALES

        domain = [
            ('product_id', '=', record.product_id.id), ('tienda_id', '=', record.tienda_id.id),
            # ("date", ">=", f"today -{sigma_dias}d"), ("date", "<=", "today"),
            ("date", ">=", limit_date), ("date", "<", today),
            # ("date", ">=", "today -30d"), ("date", "<", "today")

        ]

        historico = self.env['datawave.sale'].search(domain)
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


    #FUNCION STOCK SEGURIDAD
    def set_stock_seguridad(self):
        conf_ss = self.env['ir.config_parameter'].sudo().get_param('datawave.z_tienda')
        conf_ss = float(conf_ss) if conf_ss else 0

        if conf_ss == 1:
            import math

            # Calcular la raíz cuadrada
            raiz_cuadrada = math.sqrt(self.lt_days)
            ss = conf_ss * self.sigma * raiz_cuadrada
            self.ss = ss
        else:
            self.ss = self.lt_days * self.forecast_day

    #FUNCION FRECUENCIA
    def set_frecuency(self,conf,forecast_tienda_day,config_tienda):

        if not config_tienda:
            return

        #frecuencia fija
        if conf == 1 :
            self.freq = config_tienda.days_frequency

        if conf == 2:
            self.freq = self.lt_days + config_tienda.days_delta

        if conf == 3:
            self.freq = forecast_tienda_day.days_target

    def set_max(self,conf):

        if conf == 1 :
            self.max = ( ( self.lt_days + self.freq ) * self.freq ) + self.ss

        if conf == 2:
            self.max = (14 * self.forecast_day ) + self.ss


    def set_stock_riesgo_sobrestock(self,stock_tienda):

        self.stock = stock if stock_tienda else 0
        self.quantity = max(self.stock, self.max)

        if self.stock <= 0:
            self.riesgo = '3'

        if self.stock > 0 and self.stock < self.ss:
            self.riesgo = '2'

        if self.stock >= self.ss and self.stock < self.rop:
            self.riesgo = '1'
        if self.stock >= self.ss and self.stock >=  self.rop :
            self.riesgo = '0'


        if self.stock > self.max + self.ss :
            self.sobreestock = '2'
        else:
            if self.stock > self.max :
                self.sobreestock = '1'
            else:
                self.sobreestock = '0'

    def quantity_reponer(self, config_tienda_p):
        def multiplo_superior(numero, constante):
            if constante <= 0:
                raise ValueError("La constante debe ser mayor que 0.")
            return ((numero + constante - 1) // constante) * constante

        resultado = multiplo_superior(self.quantity, config_tienda_p.round_tienda)
        self.quantity_round = resultado


    @api.onchange('product_id','tienda_id','date')
    def change_product_tienda(self):

        conf_frecuencia_tienda = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_frecuencia_tienda')
        conf_frecuencia_tienda = int(conf_frecuencia_tienda) if conf_frecuencia_tienda else 0

        conf_max = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_max_tienda')
        conf_max = int(conf_max) if conf_max else 0



        for record in self:

            #INICIALIAR VARIABLES
            record.lt_days = 0
            record.datawave_sale_ids = False
            record.forecast_tienda_id = False
            record.lt_days = 0
            record.ss = 0
            record.freq = 0
            record.max = 0
            record.stock = 0
            record.quantity = 0
            record.riesgo = False
            record.sobreestock = False

            if not record.product_id or not record.tienda_id  or not record.date:
                continue



            #OBTENER LA CONFIGURACION DE LA TABLA CONFI_TIENDA_PRODUCTO
            config_tienda_p = self.env['datawave.config.tienda.product'].search([
                ('product_id', '=', record.product_id.id), ('tienda_id', '=', record.tienda_id.id)
            ])

            #OBTENER EL FORECAST
            forecast_tienda_day = self.env['datawave.forecast.tienda'].search([
                ('product_id', '=', record.product_id.id), ('tienda_id', '=', record.tienda_id.id)
            ])

            #stock_tienda
            domain = [
                ('tienda_id', '=', record.tienda_id.id),
                ('product_id', '=', record.product_id.id),
                ('date', '=', record.date)
            ]
            stock_tienda = self.env['datawave.stock.tienda'].search(domain)

            config_tienda = self.env['datawave.config.tienda'].search([
                ('tienda_id', '=', self.tienda_id.id)
            ])

            record.lt_days = config_tienda_p.lt_days if config_tienda_p else 0
            record.set_forecast_day(forecast_tienda_day)
            record.set_historico_sigma()
            record.set_stock_seguridad()
            record.set_frecuency(conf_frecuencia_tienda,forecast_tienda_day,config_tienda)
            record.set_max(conf_max)
            record.rop = ( record.forecast_day * record.lt_days ) + record.ss
            record.set_stock_riesgo_sobrestock(stock_tienda)
            record.quantity_reponer(config_tienda_p)










