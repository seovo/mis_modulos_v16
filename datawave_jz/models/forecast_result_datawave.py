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
        data = self.env.company.fetch_data_from_sql_server(self.env.company.get_connection_string(), stored_procedure)

        data['Date'] = pd.to_datetime(data['YearWeek'] + '1', format='%G%V%u')

        # Definir la ventana para la SMA (por ejemplo, ventana de 3 meses)
        #ventana = int(config.get('SMA', 'ventana'))
        ventana = 1

        groups = data.groupby('ProductId')

        # Recorrer los grupos
        for ProductId, DataGroup in groups:
            GroupData = DataGroup[['Date', 'TotalQuantity']]
            GroupData['Year'] = GroupData['Date'].dt.year
            GroupData['Week'] = GroupData['Date'].week
            raise ValueError(GroupData)

        raise ValueError(data)
