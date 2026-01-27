from odoo import models, fields , api
from datetime import date , datetime , timedelta


class IntermedioTienda(models.Model):
    _name = 'datawave.intermedio.tienda'
    _description = 'IntermedioTienda de Datawave'
    #name         = fields.Char(string='Clave')
    date           = fields.Date(string='Fecha', required=True)
    product_id     = fields.Many2one('datawave.producto', string='Producto', required=True)
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

    def set_forecast_day(self,forecast_tienda_day):
        record = self


        if forecast_tienda_day:
            record.forecast_tienda_id = forecast_tienda_day.id
            record.forecast_day = forecast_tienda_day.forecast_day
        else:
            record.forecast_tienda_id = None
            record.forecast_day = None

    def set_historico_sigma(self,config_tienda):

        record = self

        config = config_tienda

        # raise ValueError(config)

        if not config:
            return

        record.lt_days = config.lt_days
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


    def set_zz(self):
        conf_zz = self.env['ir.config_parameter'].sudo().get_param('datawave.z_tienda')
        conf_zz = float(conf_zz) if conf_zz else 0

        if conf_zz == 1:
            import math

            # Calcular la raíz cuadrada
            raiz_cuadrada = math.sqrt(self.lt_days)
            zz = conf_zz * self.sigma * raiz_cuadrada
            self.ss = zz
        else:
            self.ss = self.lt_days * self.forecast_day

    def set_frecuency(self,forecast_tienda_day):
        conf = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_frecuencia_tienda')
        conf = int(conf) if conf else 0

        self.freq = 0

        config_tienda = self.env['datawave.config.tienda'].search([
            ('tienda_id', '=', self.tienda_id.id)
        ])

        if not config_tienda:
            return

        #frecuencia fija
        if conf == 1 :
            self.freq = config_tienda.days_frequency

        if conf == 2:
            self.freq = self.lt_days + config_tienda.days_delta

        if conf == 3:
            self.freq = forecast_tienda_day.days_target

    def set_max(self):
        self.max = 0

        conf = self.env['ir.config_parameter'].sudo().get_param('datawave.metodo_max_tienda')
        conf = int(conf) if conf else 0

        if conf == 1 :
            self.max = ( ( self.lt_days + self.freq ) * self.freq ) + self.ss

        if conf == 2:
            self.max = (14 * self.forecast_day ) + self.ss


    def set_stock(self):
        stock = 0
        domain = [
            ('tienda_id', '=', self.tienda_id.id),
            ('product_id', '=', self.product_id.id),
            ('date', '=', self.date)
        ]
        stock_tienda = self.env['datawave.stock.tienda'].search(domain)

        if stock_tienda:
            stock = stock_tienda.stock
        # else:
        #    raise ValueError(domain)

        self.stock = stock
        self.quantity = max(self.stock, self.max)

        if self.stock <= 0:
            self.riesgo = '3'

        if self.stock > 0 and self.stock < self.ss:
            self.riesgo = '2'

        if self.stock >= self.ss and self.stock < self.rop:
            self.riesgo = '1'
        if self.stock >= self.ss and self.stock >=  self.rop :
            self.riesgo = '0'








    @api.onchange('product_id','tienda_id','date')
    def change_product_tienda(self):
        for record in self:
            record.lt_days = 0
            record.datawave_sale_ids = False

            if not record.product_id or not record.tienda_id  or not record.date:
                continue

            config_tienda_p = self.env['datawave.config.tienda.product'].search([
                ('product_id', '=', record.product_id.id), ('tienda_id', '=', record.tienda_id.id)
            ])

            forecast_tienda_day = self.env['datawave.forecast.tienda'].search([
                ('product_id', '=', record.product_id.id), ('tienda_id', '=', record.tienda_id.id)
            ])

            record.set_forecast_day(forecast_tienda_day)
            record.set_historico_sigma(config_tienda_p)
            record.set_zz()
            record.set_frecuency(forecast_tienda_day)
            record.set_max()

            record.rop = ( record.forecast_day * record.lt_days ) + record.ss


            record.set_stock()



            def multiplo_superior(numero, constante):
                if constante <= 0:
                    raise ValueError("La constante debe ser mayor que 0.")
                return ((numero + constante - 1) // constante) * constante



            resultado = multiplo_superior(record.quantity, config_tienda_p.round_tienda)
            record.quantity_round = resultado









class SigmaCD(models.Model):
    _name = 'datawave.sigma.cd'
    _description = 'SigmaCD de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    sigma  = fields.Float(string='Sigma')

class SigmaTienda(models.Model):
    _name = 'datawave.sigma.tienda'
    _description = 'SigmaTienda de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_tienda = fields.Char(string='Tienda_ID')
    sigma = fields.Float(string='Sigma')









