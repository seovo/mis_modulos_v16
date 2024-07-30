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
            #raise ValueError(str(row['Id']))
            RangeType = str(row['RangeType'])
            name_start = str(row['RangeType'])
            name_end = ''
            if RangeType == 'ABC_MC':
                name_start = 'ABC'
                name_end = '_mc'


            if RangeType == 'XYZ_MC':
                name_start = 'XYZ'
                name_end = '_mc'

            name_start = name_start.lower()


            val_start = row['RangeStart']
            val_end = row['RangeEnd']

            if str(val_start) == 'nan':
                val_start = None

            if str(val_end) == 'nan':
                val_end = None

            field_name_start = f'''{name_start}_{row['RangeString'].lower()}_start{name_end}'''
            field_name_end = f'''{name_start}_{row['RangeString'].lower()}_end{name_end}'''

            sql_update += f'''
             
             UPDATE res_company 
             SET    is_null_{field_name_start} = '{ "t" if val_start  else "f" }' ,
                    {field_name_start} = {val_start or 0} , 
                     
                    is_null_{field_name_end} = '{ "t" if val_end else 'f' }' ,
                    {field_name_end} = {val_end or 0} 
                    
             WHERE id = {self.id} ;
             
        
            '''

            #raise ValueError(sql_update)

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
                    abc_a_start = self.abc_a_start or 0
                    if  not self.is_null_abc_a_start:
                        abc_a_start = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_a_start} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")


                if 'abc_a_end' in vals:
                    update = True

                    abc_a_end = self.abc_a_end or 0
                    if  not self.is_null_abc_a_end:
                        abc_a_end = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_a_end} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")

                if 'abc_b_start' in vals:
                    update = True

                    abc_b_start = self.abc_b_start or 0

                    if  not self.is_null_abc_b_start:
                        abc_b_start = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_b_start} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")


                if 'abc_b_end' in vals:
                    update = True

                    abc_b_end  = self.abc_b_end or 0

                    if  not self.is_null_abc_b_end:
                        abc_b_end = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_b_end} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")



                if 'abc_c_start' in vals:
                    update = True
                    abc_c_start = self.abc_c_start or 0
                    if  not self.is_null_abc_c_start:
                        abc_c_start  = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_c_start} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")



                if 'abc_c_end' in vals:
                    update = True
                    abc_c_end = self.abc_c_end or 0
                    if  not self.is_null_abc_c_end:
                        abc_c_end = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_c_end} WHERE "
                            f"RangeType = 'ABC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")



                #ABC MC
                if 'abc_a_start_mc' in vals  :
                    update = True
                    abc_a_start_mc = self.abc_a_start_mc or 0

                    if  not self.is_null_abc_a_start_mc:
                        abc_a_start_mc = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_a_start_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")




                if 'abc_a_end_mc' in vals:
                    update = True

                    abc_a_end_mc = self.abc_a_end_mc or 0
                    if not self.is_null_abc_a_end_mc:
                        abc_a_end_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_a_end_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'A' AND TenantId = {self.tenant_id} ; ")



                if 'abc_b_start_mc' in vals:
                    update = True

                    abc_b_start_mc = self.abc_b_start_mc or 0

                    if  not self.is_null_abc_b_start_mc:
                        abc_b_start_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_b_start_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")



                if 'abc_b_end_mc' in vals:
                    update = True
                    abc_b_end_mc = self.abc_b_end_mc or 0
                    if   not self.is_null_abc_b_end_mc:
                        abc_b_end_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_b_end_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'B' AND TenantId = {self.tenant_id} ; ")



                if 'abc_c_start_mc' in vals:
                    update = True
                    abc_c_start_mc = self.abc_c_start_mc or 0

                    if  not self.is_null_abc_c_start_mc:
                        abc_c_start_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {abc_c_start_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")



                if 'abc_c_end_mc' in vals:
                    update = True

                    abc_c_end_mc = self.abc_c_end_mc

                    if  not self.is_null_abc_c_end_mc:
                        abc_c_end_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {abc_c_end_mc} WHERE "
                            f"RangeType = 'ABC_MC' AND RangeString = 'C' AND TenantId = {self.tenant_id} ; ")




                #xyz
                if 'xyz_x_start' in vals  :
                    update = True
                    xyz_x_start = self.xyz_x_start or 0
                    if  not self.is_null_xyz_x_start:
                        xyz_x_start = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_x_start} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_x_end' in vals:
                    update = True
                    xyz_x_end = self.xyz_x_end or 0

                    if  not self.is_null_xyz_x_end:
                        xyz_x_end = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_x_end} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_y_start' in vals:
                    update = True
                    xyz_y_start = self.xyz_y_start or 0

                    if  not self.is_null_xyz_y_start:
                        xyz_y_start  = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_y_start} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_y_end' in vals:
                    update = True

                    xyz_y_end = self.xyz_y_end or 0
                    if  not self.is_null_xyz_y_end:
                        xyz_y_end = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_y_end} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_z_start' in vals:
                    update = True
                    xyz_z_start = self.xyz_z_start or 0
                    if  not self.is_null_xyz_z_start:
                        xyz_z_start = 'NULL'
                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_z_start} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_z_end' in vals:
                    update = True

                    xyz_z_end = self.xyz_z_end or 0

                    if not self.is_null_xyz_z_end:
                        xyz_z_end = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_z_end} WHERE "
                            f"RangeType = 'XYZ' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")



                # xyz MC
                if 'xyz_x_start_mc' in vals:
                    update = True
                    xyz_x_start_mc = self.xyz_x_start_mc or 0

                    if not self.is_null_xyz_x_start_mc:
                        xyz_x_start_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_x_start_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_x_end_mc' in vals:
                    update = True

                    xyz_x_end_mc = self.xyz_x_end_mc or 0

                    if not self.is_null_xyz_x_end_mc:
                        xyz_x_end_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_x_end_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'X' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_y_start_mc' in vals:
                    update = True

                    xyz_y_start_mc = self.xyz_y_start_mc or 0

                    if not self.is_null_xyz_y_start_mc:
                        xyz_y_start_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_y_start_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_y_end' in vals:
                    update = True

                    xyz_y_end_mc = self.xyz_y_end_mc or 0

                    if not self.is_null_xyz_y_end_mc:
                        xyz_y_end_mc = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_y_end_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'Y' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_z_start_mc' in vals:
                    update = True

                    xyz_z_start_mc = self.xyz_z_start_mc or 0

                    if not self.is_null_xyz_z_start_mc:
                        xyz_z_start_mc = 'NULL'

                    sql += (f" UPDATE RangeConfigs  SET RangeStart = {xyz_z_start_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")



                if 'xyz_z_end_mc' in vals:
                    update = True

                    xyz_z_end_mc = self.xyz_z_end_mc or 0

                    if not self.is_null_xyz_z_end_mc:
                        xyz_z_end_mc = 'NULL'


                    sql += (f" UPDATE RangeConfigs  SET RangeEnd = {xyz_z_end_mc} WHERE "
                            f"RangeType = 'XYZ_MC' AND RangeString = 'Z' AND TenantId = {self.tenant_id} ; ")




                if update :

                    self.execute_sql_server(self.get_connection_string(), sql)

                    self.set_ranges_nine_box()





        return res


    def fetch_data_from_sql_server(self,connection_string, stored_procedure):
        # Connect to SQL Server
        conn = pymssql.connect(**connection_string)

        # Execute the stored procedure
        data = pd.read_sql_query(stored_procedure, conn)
        # Close the connection
        conn.close()
        return data


    def execute_sql_server(self,connection_string, query , values=None):
        # Connect to SQL Server
        conn = pymssql.connect(**connection_string)

        # Crear un objeto cursor
        cursor = conn.cursor()

        # Ejecutar una consulta SQL
        if values:
            #raise ValueError([query,values])
            cursor.executemany(query,values)
        else:
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


    def insert_querys_sql_server(self,data,table):
        del data['Id']
        insert_queries = f" truncate table {table} ; "
        values_insert = []

        headers = data.columns.tolist()
        headers += ['tenanid']

        array_s = []

        for hd in headers:
            if hd in  ['SKU','ABC','XYZ','BOX',]:
                array_s.append('%s')
            if hd in ['CANTIDAD','MONTO','ACCUMULATEDPERCENTAGE','AVG_STOCK','PRICE','STOCK_VALUE','VAL_DAY','tenanid']:
                array_s.append('%d')
        #array_s = ['%s' for _ in range(len(headers))]
        #array_s = ",".join(array_s)

        def convertir_camel_case(nombre_variable):
            #if nombre_variable == 'Id':
            #    return 'id_sql'
            if nombre_variable == 'sku':
                return 'SKU'
            if nombre_variable == 'Name':
                return 'NAME'
            if nombre_variable == 'TotalQuantitySold':
                return 'CANTIDAD'
            if nombre_variable == 'AccumulatedSaleCostPercentage':
                return 'ACCUMULATEDPERCENTAGE'

            #TotalSaleCost
            if nombre_variable == 'TotalSaleCost':
                return 'MONTO'


            #if nombre_variable == 'VariabilityPercentage':
            #    return 'gmroi'
            if nombre_variable == 'NineBox':
                return 'BOX'
            if nombre_variable == 'AverageQuantity':
                return 'AVG_STOCK'
            if nombre_variable == 'CostPerUnit':
                return 'PRICE'
            if nombre_variable == 'InventoryAverageCost':
                return 'STOCK_VALUE'
            if nombre_variable == 'StockDays':
                return 'VAL_DAY'


            # Convierte la primera letra a minúscula
            #nombre_variable = nombre_variable[0].lower() + nombre_variable[1:]
            #nombre_variable = re.sub(r'([A-Z])', r'_\1', nombre_variable).lower()

            return nombre_variable

        headers = [convertir_camel_case(nombre) for nombre in headers]

        #insert_queries += f" INSERT INTO {table} ({','.join(headers)}) VALUES ({array_s}); "

        #for index, row in data.iterrows():

        for row in data.values:
            values_insert = ''
            ctt = 0
            for rw in row:
                if type(rw)  == str :
                    values_insertx = f"  '{rw}'  "
                else:
                    values_insertx = rw

                if ctt > 0:
                    values_insert = f" , {values_insertx} "
                else:
                    values_insert = f" {values_insertx} "

                ctt += 1



            query = f" INSERT INTO {table} ({','.join(headers)}) VALUES ({values_insert}); "
            #values_insert += row.tolist() + [self.tenant_id]
            #query = f" INSERT INTO {table} ({','.join(headers)}) VALUES ({array_s}); "
            #query = f" INSERT INTO {table} ({','.join(headers)}) VALUES ({values_insert}); "
            insert_queries  +=  query
            #raise
            #values_insert += row.tolist() + [self.tenant_id]

        raise ValueError([insert_queries])

        self.execute_sql_server(self.get_connection_string(), insert_queries )


    def sync_nine_box(self):
        if self.nine_box_start_date and self.nine_box_end_date and self.nine_box_days_per_month and self.nine_box_type:
            # stored_procedure = "exec [dbo].[GetTotalNineBox] '2020-01-01' , '2020-07-31' ,  20 , 1  , 1"
            stored_procedure = f"exec [dbo].[GetTotalNineBox] '{str(self.nine_box_start_date)}' , '{self.nine_box_end_date}' ,  {self.nine_box_days_per_month} , {self.nine_box_type}  , {self.tenant_id}"
            data = self.fetch_data_from_sql_server(self.get_connection_string(), stored_procedure)
            # raise ValueError([stored_procedure,data])
            self.insert_querys(data, "total_nine_box")
            #sql = f''' truncate table BOX  ;  '''
            #self.execute_sql_server(self.get_connection_string(), sql)
            del  data['VariabilityPercentage']
            self.insert_querys_sql_server(data, 'BOX')


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



