from odoo import models, exceptions, fields , _
import pandas as pd

from datetime import datetime, timedelta

class ForecastResultDatawave(models.Model):
    _name      = "forecast.result.datawave"
    product_id = fields.Integer()
    sku        = fields.Char()
    date       = fields.Date()
    arima      = fields.Float()
    ets        = fields.Float()
    boosting   = fields.Float()
    prophet    = fields.Float()
    sma        = fields.Float()


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
            GroupData = GroupData.sort_values('Date')
            #GroupData['Year'] = GroupData['Date'].dt.year
            #GroupData['Week'] = GroupData['Date'].dt.isocalendar().week
            fecha_next = GroupData['Date'].max() + timedelta(weeks=1)

            # Calcular la SMA utilizando la función rolling de pandas
            GroupData.set_index('Date', inplace=True)
            sma = GroupData['TotalQuantity'].rolling(window=ventana).mean()

            raise ValueError(sma)
            sma.index = sma.index + pd.DateOffset(months=1)

            raise ValueError(fecha_next)

        raise ValueError(data)
