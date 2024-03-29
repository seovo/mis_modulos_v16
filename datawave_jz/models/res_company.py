from odoo import models, exceptions, fields , _

class ResCompany(models.Model):
    _inherit = "res.company"

    def test_sql_server_conexion(self):
        import pandas as pd
        import pymssql
        # import psycopg2
        # import psycopg2.extras

        def fetch_weeks_from_sql_server(connection_string, sql_query):
            # Connect to SQL Server
            conn = pymssql.connect(**connection_string)
            # Execute the SQL query to fetch the number of weeks
            cursor = conn.cursor()
            cursor.execute(sql_query)
            n_weeks = cursor.fetchone()
            # Close the cursor and connection
            cursor.close()
            conn.close()

        # Function to fetch data from SQL Server data table
        def fetch_data_from_sql_server(server, database, username, password, table_name):
            connection = pymssql.connect(server=server, database=database, user=username, password=password)

            query = f'SELECT * FROM {table_name};'
            data = pd.read_sql(query, connection)
            connection.close()

            return data

            # Configuration for SQL Server


        sql_server_config = {
            "server": "dbserverdatawave.database.windows.net",
            "database": "Datawave",
            "username": "datawaveuser",
            "password": "JT5j]6u2?XZzdw4fS#CK[pWBH!QxsD$t",
            "table_name": "Products",
        }

        #data = fetch_data_from_sql_server(**sql_server_config)

        config = {
           "connection_string": {
               "host": "dbserverdatawave.database.windows.net",
               "user": "datawaveuser",
               "password": "JT5j]6u2?XZzdw4fS#CK[pWBH!QxsD$t",
               "database": "Datawave"
            },
           "stored_procedure": "exec [dbo].[GetTotalNineBoxPerStoreMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1",
           "forecasts_table": "WeeklyForecastsByProductId",
           "sql_query_weeks": "select dbo.GetConfigurationValueAsInt('20200101' , '20200731' , 20 , 1  , 1)",
           "tenant_id": 1
        }
        connection_string = {
               "host": "dbserverdatawave.database.windows.net",
               "user": "datawaveuser",
               "password": "JT5j]6u2?XZzdw4fS#CK[pWBH!QxsD$t",
               "database": "Datawave"
        }

        stored_procedure = "exec [dbo].[GetTotalNineBoxPerStoreMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1"

        data = fetch_data_from_sql_server(connection_string, stored_procedure)

        raise ValueError(data)
        return