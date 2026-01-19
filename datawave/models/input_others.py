from odoo import models, fields

class ForecastTienda(models.Model):
    _name = 'datawave.forecast.tienda'
    _description = 'ForecastTienda de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_tienda = fields.Char(string='Tienda_ID')
    code_cd = fields.Char(string='CD_ID')
    forecast_day = fields.Integer(string='Forecast Diario')

class ForecastCD(models.Model):
    _name = 'datawave.forecast.cd'
    _description = 'ForecastCD de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    forecast_day = fields.Integer(string='Forecast Diario')