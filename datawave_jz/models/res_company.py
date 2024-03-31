from odoo import models, exceptions, fields , _

import pandas as pd
import pymssql
import re

class ResCompany(models.Model):
    _inherit = "res.company"
    sql_server_host     = fields.Char()
    sql_server_user     = fields.Char()
    sql_server_password = fields.Char()
    sql_server_database = fields.Char()

    #general
    tenant_id = fields.Integer()

    #range filters
    #ABC
    abc_a_start  = fields.Float()
    abc_a_end    = fields.Float()

    abc_b_start  = fields.Float()
    abc_b_end    = fields.Float()

    abc_c_start  = fields.Float()
    abc_c_end    = fields.Float()

    #XYZ
    xyz_x_start = fields.Float()
    xyz_x_end   = fields.Float()

    xyz_y_start = fields.Float()
    xyz_y_end   = fields.Float()

    xyz_z_start = fields.Float()
    xyz_z_end = fields.Float()

    # ABC MC
    abc_a_start_mc = fields.Float()
    abc_a_end_mc   = fields.Float()

    abc_b_start_mc = fields.Float()
    abc_b_end_mc   = fields.Float()

    abc_c_start_mc = fields.Float()
    abc_c_end_mc   = fields.Float()

    # XYZ
    xyz_x_start_mc  = fields.Float()
    xyz_x_end_mc    = fields.Float()

    xyz_y_start_mc  = fields.Float()
    xyz_y_end_mc    = fields.Float()

    xyz_z_start_mc  = fields.Float()
    xyz_z_end_mc    = fields.Float()


    #total ninebox
    nine_box_start_date     = fields.Date()
    nine_box_end_date       = fields.Date()
    nine_box_days_per_month = fields.Integer()
    nine_box_type           = fields.Integer()

    #total ninebox MC
    nine_box_mc_start_date      = fields.Date()
    nine_box_mc_end_date        = fields.Date()
    nine_box_mc_days_per_month  = fields.Integer()
    nine_box_mc_type_cost       = fields.Integer()
    nine_box_mc_type_price      = fields.Integer()


    #total nine box per store
    nine_box_per_store_start_date     = fields.Date()
    nine_box_per_store_end_date       = fields.Date()
    nine_box_per_store_days_per_month = fields.Integer()
    nine_box_per_store_type           = fields.Integer()

    #total nine box per MC
    nine_box_mc_per_store_start_date       = fields.Date()
    nine_box_mc_per_store_end_date         = fields.Date()
    nine_box_mc_per_store_days_per_month   = fields.Integer()
    nine_box_mc_per_store_type_cost        = fields.Integer()
    nine_box_mc_per_store_type_price       = fields.Integer()


    def fetch_data_from_sql_server(self,connection_string, stored_procedure):
        # Connect to SQL Server
        try:
            conn = pymssql.connect(**connection_string)
        except:
            raise ValueError(connection_string)

        # Execute the stored procedure
        data = pd.read_sql_query(stored_procedure, conn)
        # Close the connection
        conn.close()
        return data

    def get_connection_string(self):
        if not self.sql_server_host or not self.sql_server_user or self.sql_server_password or self.sql_server_database:
            #raise ValueError([self,self.sql_server_host])
            return None
        return {
            "host": self.sql_server_host,
            "user": self.sql_server_user,
            "password": self.sql_server_password,
            "database": self.sql_server_database
        }

    def insert_querys(self,data,table):
        insert_queries = f" DELETE FROM {table} ; "
        values_insert = []

        headers = data.columns.tolist()
        headers += ['CompanyId']

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
            query = f" INSERT INTO {table} ({','.join(headers)}) VALUES ({array_s}); "
            insert_queries  +=  query
            #raise
            values_insert += row.tolist() + [self.id]

        self.env.cr.execute(insert_queries, values_insert)


    def sync_nine_box(self):
        if self.nine_box_start_date and self.nine_box_end_date and self.nine_box_days_per_month and self.nine_box_type:
            # stored_procedure = "exec [dbo].[GetTotalNineBox] '2020-01-01' , '2020-07-31' ,  20 , 1  , 1"
            stored_procedure = f"exec [dbo].[GetTotalNineBox] '{str(self.nine_box_start_date)}' , '{self.nine_box_end_date}' ,  {self.nine_box_days_per_month} , {self.nine_box_type}  , {self.tenant_id}"
            data = self.fetch_data_from_sql_server(self.get_connection_string(), stored_procedure)
            # raise ValueError([stored_procedure,data])
            self.insert_querys(data, "total_nine_box")


    def sync_nine_box_mc(self):
        if self.nine_box_mc_start_date and self.nine_box_mc_end_date and self.nine_box_mc_days_per_month and self.nine_box_mc_type_cost and self.nine_box_mc_type_price:
            # "stored_procedure": "exec [dbo].[GetTotalNineBoxMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1",
            stored_procedure = f"exec [dbo].[GetTotalNineBoxMc] '{str(self.nine_box_mc_start_date)}' , '{self.nine_box_mc_end_date}' ,  {self.nine_box_mc_days_per_month} , {self.nine_box_mc_type_cost} , {self.nine_box_mc_per_store_type_price} , {self.tenant_id}"
            data = self.fetch_data_from_sql_server(self.get_connection_string(), stored_procedure)
            # raise ValueError([stored_procedure,data])
            self.insert_querys(data, "total_nine_box_mc")


    def sync_nine_box_per_store(self):
        if self.nine_box_per_store_start_date and self.nine_box_per_store_end_date and self.nine_box_per_store_days_per_month and self.nine_box_per_store_type:
            # stored_procedure": "exec [dbo].[GetTotalNineBoxPerStore] '2020-01-01' , '2020-07-31' ,  20 , 1  , 1",
            stored_procedure = f"exec [dbo].[GetTotalNineBoxPerStore] '{str(self.nine_box_per_store_start_date)}' , '{self.nine_box_per_store_end_date}' ,  {self.nine_box_per_store_days_per_month} , {self.nine_box_per_store_type}  , {self.tenant_id}"
            data = self.fetch_data_from_sql_server(self.get_connection_string(), stored_procedure)
            # raise ValueError([stored_procedure,data])
            self.insert_querys(data, "total_nine_box_per_store")


    def sync_nine_box_per_store_mc(self):
        if self.nine_box_mc_per_store_start_date and self.nine_box_mc_per_store_end_date and self.nine_box_mc_per_store_days_per_month and self.nine_box_mc_per_store_type_cost and self.nine_box_mc_per_store_type_price:
            # stored_procedure": "exec [dbo].[GetTotalNineBoxPerStoreMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1",
            stored_procedure = f"exec [dbo].[GetTotalNineBoxPerStoreMc] '{str(self.nine_box_mc_per_store_start_date)}' , '{self.nine_box_mc_per_store_end_date}' ,  {self.nine_box_mc_per_store_days_per_month} , {self.nine_box_mc_per_store_type_cost} , {self.nine_box_mc_per_store_type_price} , {self.tenant_id}"
            data = self.fetch_data_from_sql_server(self.get_connection_string(), stored_procedure)
            # raise ValueError([stored_procedure,data])
            self.insert_querys(data, "total_nine_box_per_store_mc")


    def test_sql_server_conexion(self):
        connection_string = {
            "host": self.sql_server_host,
            "user": self.sql_server_user,
            "password": self.sql_server_password,
            "database": self.sql_server_database
        }


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


    def sync_nine_box_range_date(self):
        raise ValueError(self.env.company.get_connection_string())
        if not  self.get_connection_string():
            return
        data = self.fetch_data_from_sql_server(self.get_connection_string(), f'SELECT * FROM RangeConfigs;')
        raise ValueError(data)
