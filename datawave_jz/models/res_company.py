from odoo import models, exceptions, fields , _

class ResCompany(models.Model):
    _name = "res.company"

    def test_sql_server_conexion(self):
        import pandas as pd
        import pymssql
        # import psycopg2
        # import psycopg2.extras

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

        data = fetch_data_from_sql_server(**sql_server_config)

        raise ValueError(data)
        return