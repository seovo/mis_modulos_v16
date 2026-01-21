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
    forecast_day   = fields.Integer(string='Forecast Diario')
    sigma          = fields.Float(string='Sigma')
    ss             = fields.Float(string='SS',help='Z*Sigma*SQRT(LT)')
    freq           = fields.Float(string='FREQ')
    max            = fields.Float(string='MAX',help='(LT+FREQ)*Forecast+SS')
    rop            = fields.Float(string='ROP',help='Forecast*LT+SS')
    stock          = fields.Integer(string='Stock')
    quantity       = fields.Integer(string='Cantidad Sugerida',help='MAX(0,MAX-Stock)')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')

    @api.onchange('product_id','tienda_id','date')
    def change_product_tienda(self):
        for record in self:
            record.lt_days = 0



            if not record.product_id or not record.tienda_id:
                continue

            config = self.env['datawave.config.tienda.product'].search([
                ('product_id','=',record.product_id.id),('tienda_id','=',record.tienda_id.id)
            ])

            #raise ValueError(config)


            if not config:
                continue

            record.lt_days = config.lt_days

            sigma_dias = self.env['ir.config_parameter'].sudo().get_param('datawave.ventana_sigma_dias')

            sigma_dias = int(sigma_dias) if sigma_dias else 0




            today = record.date
            limit_date = today - timedelta(days=sigma_dias)


            #DIAS LOBORALES

            domain = [
                ('product_id','=',record.product_id.id),('tienda_id','=',record.tienda_id.id),
                #("date", ">=", f"today -{sigma_dias}d"), ("date", "<=", "today"),
                ("date", ">=", limit_date), ("date", "<", today),
                #("date", ">=", "today -30d"), ("date", "<", "today")

            ]

            historico = self.env['datawave.sale'].search(domain)
            #raise ValueError(historico)
            if historico:
                import statistics
                datos = []
                for hist in historico:
                    datos.append(hist.quantity)
                #raise ValueError(datos)
                desviacion_estandar_poblacional = statistics.pstdev(datos)
                #raise ValueError(desviacion_estandar_poblacional)
                record.sigma = desviacion_estandar_poblacional
            else:
                raise ValueError(domain)






class IntermedioCD(models.Model):
    _name = 'datawave.intermedio.cd'
    _description = 'IntermedioCD de Datawave'
    name         = fields.Char(string='Clave')
    code         = fields.Char(string='Clave2')
    sku          = fields.Char(string='Producto_ID')
    code_cd      = fields.Char(string='CD_ID')
    code_seller  = fields.Char(string='Proveedor ID')
    lt_days      = fields.Integer(string='LT Dias')
    forecast_day = fields.Integer(string='Forecast Diario')
    sigma        = fields.Float(string='Sigma')
    moq          = fields.Float(string='Sigma')
    stock        = fields.Integer(string='Stock')
    stock_transit = fields.Integer(string='Stock Transito')
    stock_forecast = fields.Integer(string='Stock Pronosticado')
    ss = fields.Float(string='SS', help='Z*Sigma*SQRT(LT)')
    freq = fields.Float(string='FREQ')
    max = fields.Float(string='MAX', help='(LT+FREQ)*Forecast+SS')
    rop = fields.Float(string='ROP', help='Forecast*LT+SS')
    quantity = fields.Integer(string='Cantidad Sugerida', help='MAX(0,MAX-Stock)')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')



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









