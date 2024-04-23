from odoo import models, exceptions, fields , _
import pandas as pd

class ForecastResultDatawave(models.Model):
    _name    = "forecast.result.datawave"
    sku      = fields.Char()
    arima    = fields.Float()
    ets      = fields.Float()
    boosting = fields.Float()
    prophet  = fields.Float()
    sma      = fields.Float()


    def sync_datawave(self):
        stored_procedure = f"exec [dbo].[GetDataToFeedWeeklyForecastByProductId] {self.env.company.tenant_id}"
        sales_data = self.env.company.fetch_data_from_sql_server(self.env.company.get_connection_string(), stored_procedure)

        sales_data['FECHA'] = pd.to_datetime(sales_data['YearWeek'] + '01', format='%Y%m%d')
        raise ValueError(sales_data)
