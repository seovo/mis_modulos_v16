from odoo import models, exceptions, fields , _

class ResCompany(models.Model):
    _inherit = "res.company"

    def test_sql_server_conexion(self):
        import pandas as pd
        import pymssql
        import re
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
        def fetch_data_from_sql_server(connection_string, stored_procedure):
            # Connect to SQL Server
            conn = pymssql.connect(**connection_string)
            # Execute the stored procedure
            data = pd.read_sql_query(stored_procedure, conn)
            # Close the connection
            conn.close()
            return data


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

        insert_queries = ""
        values_insert = []


        headers = data.columns.tolist()

        array_s = ['%s' for _ in range(len(headers))]
        array_s = ",".join(array_s)

        def convertir_camel_case(nombre_variable):
            if nombre_variable == 'Id':
                return 'id_sql'
            if nombre_variable == 'sku':
                return 'sku'
            if nombre_variable == 'Name':
                return 'name'
            if nombre_variable == 'ABC':
                return 'abc'
            if nombre_variable == 'XYZ':
                return 'xyz'
            if nombre_variable == 'GMROI':
                return 'gmroi'
            # Convierte la primera letra a minúscula
            nombre_variable = nombre_variable[0].lower() + nombre_variable[1:]
            nombre_variable = re.sub(r'([A-Z])', r'_\1', nombre_variable).lower()

            return nombre_variable

        headers = [convertir_camel_case(nombre) for nombre in headers]

        #for index, row in data.iterrows():
        for row in data.values:
            query = f" INSERT INTO total_nine_box_per_store_mc ({','.join(headers)}) VALUES ({array_s}); "
            insert_queries  +=  query
            #raise
            values_insert += row.tolist()

        self.env.cr.execute(insert_queries, values_insert)

        #raise ValueError(data)
        return