from odoo import models, exceptions, fields , _

class ForecastResultDatawave(models.Model):
    _name    = "forecast.result.datawave"
    sku      = fields.Char()
    arima    = fields.Float()
    ets      = fields.Float()
    boosting = fields.Float()
    prophet  = fields.Float()
    sma      = fields.Float()


    def sync_datawave(self):
        stored_procedure = f"exec [dbo].[GetDataToFeedWeeklyForecastByProductId] {self.tenant_id}"
        data = self.env.company.fetch_data_from_sql_server(self.env.company.get_connection_string(), stored_procedure)
        raise ValueError(data)
