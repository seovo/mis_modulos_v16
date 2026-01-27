from odoo import models, fields

class ForecastTienda(models.Model):
    _name = 'datawave.forecast.tienda'
    _description = 'ForecastTienda de Datawave'
    #name = fields.Char(string='Clave')
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    tienda_id = fields.Many2one('datawave.tienda', string='Tienda', required=True)
    cd_id = fields.Many2one('datawave.cd', string='CD',related='tienda_id.cd_id')
    forecast_day = fields.Float(string='Forecast Diario')

class ForecastCD(models.Model):
    _name = 'datawave.forecast.cd'
    _description = 'ForecastCD de Datawave'

    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    cd_id = fields.Many2one('datawave.cd', string='CD')
    forecast_day = fields.Integer(string='Forecast Diario')