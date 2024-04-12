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
    is_null_abc_a_start = fields.Boolean()
    abc_a_start         = fields.Float()
    is_null_abc_a_end   = fields.Boolean()
    abc_a_end           = fields.Float()

    is_null_abc_b_start = fields.Boolean()
    abc_b_start         = fields.Float()
    is_null_abc_b_end   = fields.Boolean()
    abc_b_end           = fields.Float()

    is_null_abc_c_start = fields.Boolean()
    abc_c_start         = fields.Float()
    is_null_abc_c_end   = fields.Boolean()
    abc_c_end           = fields.Float()

    #XYZ
    is_null_xyz_x_start = fields.Boolean()
    xyz_x_start         = fields.Float()
    is_null_xyz_x_end   = fields.Boolean()
    xyz_x_end           = fields.Float()

    is_null_xyz_y_start = fields.Boolean()
    xyz_y_start         = fields.Float()
    is_null_xyz_y_end   = fields.Boolean()
    xyz_y_end           = fields.Float()

    is_null_xyz_z_start = fields.Boolean()
    xyz_z_start         = fields.Float()
    is_null_xyz_z_end   = fields.Boolean()
    xyz_z_end           = fields.Float()

    # ABC MC
    is_null_abc_a_start_mc = fields.Boolean()
    abc_a_start_mc         = fields.Float()
    is_null_abc_a_end_mc   = fields.Boolean()
    abc_a_end_mc           = fields.Float()

    is_null_abc_b_start_mc = fields.Boolean()
    abc_b_start_mc         = fields.Float()
    is_null_abc_b_end_mc   = fields.Boolean()
    abc_b_end_mc           = fields.Float()

    is_null_abc_c_start_mc = fields.Boolean()
    abc_c_start_mc         = fields.Float()
    is_null_abc_c_end_mc   = fields.Boolean()
    abc_c_end_mc           = fields.Float()

    # XYZ MC
    is_null_xyz_x_start_mc = fields.Boolean()
    xyz_x_start_mc         = fields.Float()
    is_null_xyz_x_end_mc   = fields.Boolean()
    xyz_x_end_mc           = fields.Float()

    is_null_xyz_y_start_mc = fields.Boolean()
    xyz_y_start_mc         = fields.Float()
    is_null_xyz_y_end_mc   = fields.Boolean()
    xyz_y_end_mc           = fields.Float()

    is_null_xyz_z_start_mc = fields.Boolean()
    xyz_z_start_mc         = fields.Float()
    is_null_xyz_z_end_mc   = fields.Boolean()
    xyz_z_end_mc           = fields.Float()


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


    def set_ranges_nine_box(self):

        query = f"SELECT * FROM RangeConfigs WHERE TenantId = {self.tenant_id} ; "
        data = self.fetch_data_from_sql_server(self.get_connection_string(), query )

        sql_update = ''

        for index, row in data.iterrows():
            raise ValueError(str(row))
            RangeType = row['ID']
            name_start = row['ID']
            name_end = ''
            if RangeType == 'ABC_MC':
                name_start = 'ABC'
                name_end = '_mc'


            if RangeType == 'XYZ_MC':
                name_start = 'XYZ'
                name_end = '_mc'

            name_start = name_start.lower()


            val_start = row['RangeStart']
            val_end = row['RangeStart']

            field_name_start = f'''{name_start}_{row['RangeString'].lower()}_start_{name_end}'''
            field_name_end = f'''{name_start}_{row['RangeString'].lower()}_end_{name_end}'''

            sql_update += f'''
             
             UPDATE res_company 
             SET    is_null_{field_name_start} = { 't' if val_start else 'f' } ,
                    {field_name_start} = {val_start or 0} , 
                     
                    is_null_{field_name_end} = { 't' if val_end else 'f' } ,
                    {field_name_end} = {val_end or 0} 
                    
             WHERE id = {self.id} ;
             
        
            '''

        if sql_update != '':
            self.env.cr.execute(sql_update)

    def write(self,vals):
        #raise ValueError(vals)
        res = super().write(vals)





        if len(self) == 1:
            if self.tenant_id :


                if 'nine_box_start_date' in vals or 'nine_box_end_date' in vals or 'nine_box_days_per_month' in vals or 'nine_box_type' in vals:
                    self.sync_nine_box()

                if 'nine_box_mc_start_date' in vals or 'nine_box_mc_end_date' in vals or 'nine_box_mc_days_per_month' in vals or 'nine_box_mc_type_cost' in vals or 'nine_box_mc_type_price' in vals:
                    self.sync_nine_box_mc()

                if 'nine_box_per_store_start_date' in vals or 'nine_box_per_store_end_date' in vals or 'nine_box_per_store_days_per_month' in vals or 'nine_box_per_store_type' in vals:
                    self.sync_nine_box_per_store()

                if 'nine_box_mc_per_store_start_date' in vals or 'nine_box_mc_per_store_end_date' in vals or 'nine_box_mc_per_store_days_per_month' in vals or 'nine_box_mc_per_store_type_cost' in vals or 'nine_box_mc_per_store_type_price' in vals:
                    self.sync_nine_box_per_store_mc()

                ######################3

                sql = ''
                update = False
                if 'abc_a_start' in vals  :
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_a_start or 0} WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")


                if 'abc_a_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_a_end or 0 } WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")

                if 'abc_b_start' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_b_start or 0} WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")

                if 'abc_b_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_b_end or 0} WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")

                if 'abc_c_start' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_c_start or 0} WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")

                if 'abc_c_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_c_end or 0} WHERE "
                        f"RangeType = 'ABC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")

                #ABC MC
                if 'abc_a_start_mc' in vals  :
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_a_start_mc or 0} WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")


                if 'abc_a_end_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_a_end_mc or 0 } WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")

                if 'abc_b_start_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_b_start_mc or 0} WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")

                if 'abc_b_end_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_b_end_mc or 0} WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")

                if 'abc_c_start_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.abc_c_start_mc or 0} WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")

                if 'abc_c_end_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.abc_c_end_mc or 0} WHERE "
                        f"RangeType = 'ABC_MC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")


                #xyz
                if 'xyz_x_start' in vals  :
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_x_start or 0} WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")


                if 'xyz_x_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_x_end or 0 } WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_y_start' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_y_start or 0} WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_y_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_y_end or 0} WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_z_start' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_z_start or 0} WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_z_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_z_end or 0} WHERE "
                        f"RangeType = 'XYZ' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")

                # xyz MC
                if 'xyz_x_start_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_x_start_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_x_end_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_x_end_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_y_start_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_y_start_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_y_end' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_y_end_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_z_start_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeStart = {self.xyz_z_start_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")

                if 'xyz_z_end_mc' in vals:
                    update = True

                sql += (f" UPDATE RangeConfigs  SET RangeEnd = {self.xyz_z_end_mc or 0} WHERE "
                        f"RangeType = 'XYZ_MC' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")




                if update :

                    self.execute_sql_server(self.get_connection_string(), sql)





        return res


    def fetch_data_from_sql_server(self,connection_string, stored_procedure):
        # Connect to SQL Server
        conn = pymssql.connect(**connection_string)

        # Execute the stored procedure
        data = pd.read_sql_query(stored_procedure, conn)
        # Close the connection
        conn.close()
        return data


    def execute_sql_server(self,connection_string, query):
        # Connect to SQL Server
        conn = pymssql.connect(**connection_string)

        # Crear un objeto cursor
        cursor = conn.cursor()

        # Ejecutar una consulta SQL
        cursor.execute(query)

        conn.commit()
        cursor.close()

        # Cerrar la conexión
        conn.close()

        return

    def get_connection_string(self):

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



