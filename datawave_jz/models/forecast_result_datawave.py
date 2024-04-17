from odoo import models, exceptions, fields , _

class ForecastResultDatawave(models.Model):
    _name    = "forecast.result.datawave"
    sku      = fields.Char()
    arima    = fields.Float()
    ets      = fields.Float()
    boosting = fields.Float()
    prophet  = fields.Float()
    sma      = fields.Float()
