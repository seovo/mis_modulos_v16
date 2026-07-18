from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql

class MigrateModelJz(models.Model):
    _name = 'migrate.model.jz'
    model_id = fields.Many2one('ir.model',string="Modelo")
    table = fields.Char(required=True)
    new_table = fields.Char(string="Nueva Tabla")
    columns = fields.One2many('migrate.model.columns.jz','migrate_model_id')
    log = fields.Text()
    migrate_id = fields.Many2one('migrate.jz')
    name = fields.Char(related='table')
    update_if_exist = fields.Boolean(string="Actualizar si Existe")
    ignorar_if_error = fields.Boolean(string="Ignorar si Error")
    no_existe_id = fields.Boolean()
    where_set = fields.Text()
    identificador = fields.Char(default='id')
    sequence = fields.Integer(string="Sequence", default=10)
    show_data = fields.Boolean(string='Mostrar Data')

    is_part_cron = fields.Boolean(string='Ejecutar por Lotes Cron')
    last_value = fields.Integer(string='Ultimo Registro Ejecutado %LAST')
    records_value = fields.Integer(string="Numero de Registros %NUM_RECORDS ",default=200)


    @api.onchange('model_id')
    def change_model(self):
        for record in self:
            if record.model_id:
                table = record.model_id.model.replace('.','_')
                #raise ValueError(table)
                record.table = table

    @api.onchange('table')
    def change_table(self):
        table = self.table
        cursor = self.migrate_id.conect_postgres()

        string_sql = f"SELECT * FROM {table} LIMIT 1"
        try:
            cursor.execute(string_sql)

        except:
            #cursor.execute(string_sql)
            self.columns = None
            return

        self.columns = None

        if  '_rel' in self.table:
            self.no_existe_id = True

        columns_current = None
        list_field_current = []

        if self.model_id:
            if self.model_id.field_id:
                for field_current in self.model_id.field_id:
                    list_field_current.append(field_current.name)

        list_field_insert = []


        for desc in cursor.description:

            #if desc[0] == 'name':
            #    raise ValueError(desc[1])
            dx = {
                'migrate_model_id' : self.id ,
                'name': desc[0] ,
                'ignore': False
            }

            if list_field_current:
                if desc[0] not in list_field_current:
                    dx.update({'ignore': True})



            if desc[1] == 3802 :
                dx.update({'type_field':'jsonb_text'})


            if table in ['res_partner']:
                if desc[0] == 'display_name':
                    dx.update({
                        'name': 'complete_name',
                        'value_set': 'display_name as complete_name'
                    })

                if desc[0] in ['create_uid' , 'write_uid'] :
                    dx.update({'ignore': True})

                if desc[0] in ['commercial_partner_id','parent_id'] :
                    dx.update({'ignore': True})

                if desc[0] in ['user_id'] :
                    dx.update({'ignore': True})



            #if table in ['account_invoice_line']:
            #    dx.update({'ignore': True})


            self.env['migrate.model.columns.jz'].create(dx)

            if dx['ignore'] != True:
                list_field_insert.append(dx['name'])


        if table == 'res_partner':
            if 'autopost_bills' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'autopost_bills' ,
                    'value_set': "'ask'",
                    'migrate_model_id': self.id,
                })

        if table == 'product_template':
            if 'service_tracking' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'service_tracking' ,
                    'value_set': "'no'",
                    'migrate_model_id': self.id,
                })




    def migrate_table(self):

        case_sql = None

        cursor = self.migrate_id.conect_postgres()
        table = self.new_table or self.table


        #ESTO NO SE ESTA USANDO
        if ',' in self.identificador :


            name_constraint = 'TEMPORAL_'+table

            queryy = f"""
                ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name_constraint};
                ALTER TABLE  {table}
                ADD CONSTRAINT {name_constraint}
                UNIQUE  ({self.identificador});
            """
            #self.env.cr.execute(queryy)
            


        select_columnsx = []
        column_names = []

        for colx in self.columns:
            #raise ValueError([col,col.ignore])
            ignorar = False
            if colx.ignore == True:
                ignorar = True

            if table == 'res_partner':
                if self.update_if_exist:
                    if colx.name in ['parent_id']:
                        ignorar = False

            if ignorar:
                continue

            namm = f'"{colx.name}"'



            column_names.append(namm)

            if colx.type_field in ['text_jsonb']:
                #namm += '::jsonb'
                namm = f'''
                jsonb_build_object(
                    'en_US', {colx.name},
                    'es_PE', {colx.name}
                )::text AS {namm}
                '''


            if colx.type_field in ['jsonb_text']:
                namm += '::text'
                #namm = f''' '"' || jsonb_to_json({namm}) || '"' AS {namm}_json '''
            if colx.value_set :
                namm = f'''{colx.value_set} '''

            if colx.is_field:
                if not case_sql:

                    insert_case =  ''
                    for line in self.migrate_id.field_ids:
                        if line.ir_model_fields_id:
                            insert_case += f''' WHEN {line.id_sql} IS NULL   THEN {line.ir_model_fields_id.id}  '''


                    case_sql = f'''
                    CASE
                    {insert_case}
                    END AS field
                    '''

                namm = case_sql

            select_columnsx.append(namm)
            #if colx.ignore :
            #    raise ValueError([colx,colx.ignore,colx.name])


        #raise ValueError(select_columnsx)

        self._migrate_table(cursor, select_columnsx,column_names)


        #ESTO NO SE ESTA USANDO
        '''
        if ',' in self.identificador:
            queryy += f"""
                alter table {table}
                drop constraint {name_constraint};
            """
            #self.env.cr.execute(queryy)
        '''
            


    def _migrate_table(self,cursor,select_columns,column_names):
        table = self.table
        #raise ValueError(select_columns)
        #select_columns = [f'"{element}"' for element in select_columns]
        string_columns = ",".join(select_columns)
        #quitar limit
        string_sql = f"SELECT {string_columns} FROM {table} "
        if table == 'res_users':
            add_where = f' AND {self.where_set}   ' if self.where_set else ''
            string_sql += f'  where id != {self.env.user.id} {add_where} ;'
        else:
            if self.where_set:

                where_set = self.where_set

                if '%LAST' in where_set:
                    where_set = where_set.replace('%LAST',str(self.last_value))

                if '%NUM_RECORDS' in where_set:
                    where_set = where_set.replace('%NUM_RECORDS',str(self.records_value))

                string_sql += f'  where {where_set} ;'


        #raise ValueError(string_sql)

        cursor.execute(string_sql)

        #try:
        #    cursor.execute(string_sql)
        #except:
        #    raise ValueError(string_sql)

        #version 12

        if self.migrate_id.from_version == 12:
            if self.table == 'product_attribute_value_product_product_rel':
                self.insert_product_variant_combination( cursor, table, column_names)
            else:
                self.insert_record_migrate(cursor, table, column_names)
        else:
            self.insert_record_migrate(cursor, table, column_names)

        if  self.where_set and '%LAST' in self.where_set:
            self.last_value = self.last_value + self.records_value



        #resultados = cursor.fetchall()

    def insert_product_variant_combination(self, cursor, table, column_names):
        resultados = cursor.fetchall()

        insert_sql = ''

        for fila in resultados:

            product = self.env['product.product'].browse(fila[0])

            sql = f'''
            SELECT id , attribute_line_id
                FROM product_template_attribute_value 
                WHERE product_attribute_value_id = {fila[1]}
                AND  product_tmpl_id  = {product.product_tmpl_id.id}
               
            '''


            self.env.cr.execute(sql)
            data =  self._cr.fetchall()
            if data:

                SQL_INSERT = f'''
                       INSERT INTO product_variant_combination(product_product_id,product_template_attribute_value_id)
                       VALUES ({fila[0]},{data[0][0]}) ON CONFLICT (product_product_id,product_template_attribute_value_id) DO NOTHING ; 
                '''
                self.env.cr.execute(SQL_INSERT)
                #SQL_INSERT = f'''
                #    INSERT INTO product_attribute_value_product_template_attribute_line_rel(product_attribute_value_id,product_template_attribute_line_id)
                #    VALUES ({fila[1]},{data[0][1]}) ON CONFLICT (product_attribute_value_id,product_template_attribute_line_id) DO NOTHING ;
                #'''

                #self.env.cr.execute(SQL_INSERT)

                #product_attribute_value_id
                #product_template_attribute_line_id


                #raise ValueError([data, sql])


    def insert_record_migrate(self,cursor,table,column_names):

        if self.new_table:
            table = self.new_table

        #column_names = [f'"{element}"' for element in column_names]

        resultados = cursor.fetchall()  # Obtener todos los resultados

        #if self.show_data:
        #    raise ValueError(resultados)

        if self.table == 'account_journal':

            for journal in resultados:
                # raise ValueError(journal)
                journal_migration = self.env['journal.migration.jz'].search([
                    ('migrate_id','=',self.migrate_id.id),
                    ('id_sql','=', int(journal[0]))
                ])

                name_journal = str(journal[1])

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': name_journal,
                    'id_sql': int(journal[0])
                     # 'journal_id':
                }

                exist_diario = self.env['account.journal'].search([('name','ilike',name_journal)])

                if len(exist_diario) > 1 :
                    exist_diario = None

                if exist_diario:
                    data_insert.update({
                        'journal_id'  : exist_diario.id
                    })

                if not journal_migration:
                    self.env['journal.migration.jz'].create(data_insert)
                else:
                    journal_migration.write(data_insert)


            #if not self.migrate_id.journal_migration_ids:
            #raise ValidationError('Contabilidad')

            return

        if self.table == 'res_currency':



            if not self.migrate_id.currency_migration_ids:
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['currency.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'name': str(journal[1]) ,
                        'id_sql': int(journal[0])
                        #'journal_id':
                    })
            #raise ValidationError('Contabilidad')

            return


        if self.table == 'account_tax':



            #raise ValueError({
            #    'a': column_names,
            #    'b': resultados[0]
            #})

            #esto solo esta probado en odoo12
            #raise ValueError(column_names)
            position_description  = column_names.index('"description"')
            position_type_tax_use = column_names.index('"type_tax_use"')
            position_amount       = column_names.index('"amount"')
            position_name         = column_names.index('"name"')

            #raise ValueError(resultados[0][position_description])

            tax_use_ids = []




            for result_tax in resultados:
                # REALIZAR LA MIGRACION AQUI
                # raise ValueError(journal)



                value_description = result_tax[position_description]
                value_type_tax_use = result_tax[position_type_tax_use]
                value_amount = result_tax[position_amount]
                value_name = result_tax[position_name]

                #VALIDACION DESCRIPCION / NOMBRE E IMPUESTO
                dominio_tax = [
                    ('type_tax_use', '=', value_type_tax_use),
                    ('amount', '=', value_amount),
                    #('tax_migration_jz_ids', '=', False),
                    ('description', 'ilike', value_name)
                ]

                exist_tax = self.env['account.tax'].search(dominio_tax)



                if len(exist_tax) > 1:
                    exist_tax = None

                #VALIDACION DESCRIPCION
                if not exist_tax:
                    # VALIDACION DESCRIPCION / NOMBRE E IMPUESTO
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('description', 'ilike', value_name)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    if len(exist_tax) > 1:
                        exist_tax = None



                #VALIDACION PORCENTAJE

                if not exist_tax:
                    # Validacion solo por porcentaje

                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        #('tax_migration_jz_ids', '=', False),

                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    # if value_description == '2% ISC':
                    #    raise V

                    if len(exist_tax) > 1:
                        exist_tax = None

                #if value_name == '18% ITBIS Compras':
                #    raise ValueError([exist_tax,tax_use_ids])

                if not exist_tax:
                    exist_tax = None



                if exist_tax:
                    tax_use_ids.append(exist_tax.id)
                    exist_tax = exist_tax.id


                if exist_tax in tax_use_ids:
                    exist_tax = None

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': value_name,
                    'id_sql': int(result_tax[0]),
                    'type': value_type_tax_use ,
                    'amount': value_amount ,
                    'tax_id': exist_tax
                }





                tax_migration = self.env['tax.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', int(result_tax[0]))
                ])

                if not tax_migration:
                    tax_migration = self.env['tax.migration.jz'].create(data_insert)
                else:
                    tax_migration.write(data_insert)


            #REALIZAR UNA SEGUNDA BUSQUEDA
            for result_tax in resultados:
                # REALIZAR LA MIGRACION AQUI
                # raise ValueError(journal)



                value_description = result_tax[position_description]
                value_type_tax_use = result_tax[position_type_tax_use]
                value_amount = result_tax[position_amount]
                value_name = result_tax[position_name]



                # VALIDACION DESCRIPCION / NOMBRE E IMPUESTO
                dominio_tax = [
                    ('type_tax_use', '=', value_type_tax_use),
                    ('amount', '=', value_amount),
                    ('tax_migration_jz_ids', '=', False),
                    ('description', 'ilike', value_name),
                    #('id','not in',tax_use_ids)
                ]

                exist_tax = self.env['account.tax'].search(dominio_tax)

                #if value_name == '18% ITBIS Compras':
                #    raise ValueError([exist_tax,tax_use_ids])

                if len(exist_tax) > 1:
                    exist_tax = None

                if exist_tax in tax_use_ids:
                    exist_tax = None

                if exist_tax:


                    tax_use_ids.append(exist_tax.id)

                    tax_migration = self.env['tax.migration.jz'].search([
                        ('migrate_id', '=', self.migrate_id.id),
                        ('id_sql', '=', int(result_tax[0]))
                    ])

                    tax_migration.write({'tax_id': exist_tax.id })








            #raise ValidationError('Contabilidad')

            return



        if self.table == 'account_account':

            if not self.migrate_id.account_migration_ids:
                #raise ValidationError(str(resultados))
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['account.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'name': str(journal[1]) ,
                        'id_sql': int(journal[0]) ,
                        'code': str(journal[3]) ,
                        #'journal_id':
                    })
            #raise ValidationError('Contabilidad')

            return

        if self.table == 'stock_location':

            if not self.migrate_id.location_migration_ids:
                #raise ValidationError(str(resultados))
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['location.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'name': str(journal[1]) ,
                        'id_sql': int(journal[0]) ,
                        #'code': str(journal[3]) ,
                        #'journal_id':
                    })
            #raise ValidationError('Contabilidad')

            return

        if self.table == 'res_country':
            if not self.migrate_id.country_migration_ids:
                #raise ValidationError(str(resultados))
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['country.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'id_sql': int(journal[0]),
                        'name': str(journal[1])
                    })
            return

        if self.table == 'res_country_state':
            if not self.migrate_id.state_migration_ids:
                #raise ValidationError(str(resultados))
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['state.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'id_sql': int(journal[0]),
                        'name': str(journal[1])
                    })
            return

        if self.table == 'city_migration_jz':
            if not self.migrate_id.city_migration_ids:
                #raise ValidationError(str(resultados))
                for journal in resultados:
                    #raise ValueError(journal)
                    self.env['city.migration.jz'].create({
                        'migrate_id': self.migrate_id.id ,
                        'id_sql': int(journal[0]),
                        'name': str(journal[1])
                    })
            return

        if self.last_value <= 0 :
            if self.table == 'product_taxes_rel':
                self.env.cr.execute("TRUNCATE TABLE product_taxes_rel ;")

            if self.table == 'product_supplier_taxes_rel':
                self.env.cr.execute("TRUNCATE TABLE product_supplier_taxes_rel ;")

            if self.table == 'account_tax_purchase_order_line_rel':
                self.env.cr.execute("TRUNCATE TABLE account_tax_purchase_order_line_rel ;")




        #raise ValueError(column_names)

        n = len(column_names)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('%s' for _ in range(n))

        identificador = self.identificador

        # Generar la instrucción INSERT

        for fila in resultados:
            val1 = ','.join(column_names)
            val2 = corchetes_n




            '''
            if self.table == 'account_invoice':

                valores = []
                id_update = 0

                for coln in column_names:
                    pass


                SQL_INSERT = f"UPDATE account_move SET x_invoice_id = %s WHERE id = %s";
                self.env.cr.execute(SQL_INSERT, fila)

                #raise ValueError([fila,column_names])

                continue
                
            '''


            if self.no_existe_id:
                if self.ignorar_if_error:
                    conflict = val1.replace('"','')
                    #SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2})  ON CONFLICT ({conflict}) DO NOTHING  "
                    SQL_INSERT = f'''
                    DO $$
BEGIN
    INSERT INTO {table} ({val1}) VALUES ({val2})  ON CONFLICT ({conflict}) DO NOTHING ;
    
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE NOTICE 'Error: El registro de invoice_line_id no existe. Ignorando...';
    WHEN others THEN
        RAISE NOTICE 'Se produjo un error inesperado. Ignorando...';
        
END $$;
                    '''
                else:
                    SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) "



            else:
                if self.update_if_exist:

                    if ',' in identificador:

                        #identicators = identificador.split(',')
                        #identificadors = []

                        #for line in identicators:
                        #    identificadors.append(line.strip())
                        #raise ValueError([identificadors,column_names])


                        if table == 'account_move_line' and self.table ==  'account_invoice_line':
                            #SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND name = %s AND price_unit != 0"

                            SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND name = %s"



                            self.env.cr.execute(SQL_CONSULTA,[fila[0],fila[1]])
                            result = self.env.cr.fetchall()

                            #raise ValueError(result)

                            #if not result:
                            #    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND POSITION(%s IN name) > 0  AND price_unit != 0 "
                            #    self.env.cr.execute(SQL_CONSULTA, [fila[0], fila[1][:20]])
                            #    result = self.env.cr.fetchall()

                            #if not result:
                            #    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND POSITION(%s IN name) > 0  AND price_unit != 0 "
                            #    self.env.cr.execute(SQL_CONSULTA, [fila[0], fila[1][5:25]])
                            #    result = self.env.cr.fetchall()


                            #if not result:
                            #    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND POSITION(%s IN name) > 0  AND price_unit != 0 "
                            #    self.env.cr.execute(SQL_CONSULTA, [fila[0], fila[1][:10]])
                            #    result = self.env.cr.fetchall()



                            #raise ValueError([result,SQL_CONSULTA,[fila[0],fila[1]]])

                            if not result or len(result) > 1:

                                if fila[3]:
                                    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND product_id = %s "

                                    self.env.cr.execute(SQL_CONSULTA, [fila[0], fila[3]])
                                    result = self.env.cr.fetchall()

                                    if self.show_data:
                                        raise ValueError([result, SQL_CONSULTA, [fila[0], fila[3], fila]])
                                else:

                                    lines = self.env['account.move.line'].search([('x_invoice_id','=',fila[0]),('name','ilike',fila[1])])
                                    result = []
                                    if lines:
                                        for ln in lines:
                                            result.append(ln.id)
                                            #ln.price_unit = fila[2]

                                    #raise ValidationError(lines)

                                    #SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s"

                                    #self.env.cr.execute(SQL_CONSULTA, [fila[0]])
                                    #result = self.env.cr.fetchall()
                                    #raise ValidationError(str([result,fila[1]]))




                                #if result and len(result) > 1:
                                #    result = result[0]





                            if not result:
                                continue
                            #raise ValueError([result])

                            for rr in result:
                                SQL_INSERT = f'''

                                                            UPDATE {table}
                                                            SET  price_unit = %s
                                                            WHERE  id = %s 

                                                            '''

                                self.env.cr.execute(SQL_INSERT, [fila[2], rr])
                                # cursor.execute(SQL_INSERT, [fila[2],fila[0],fila[1]])
                            continue




                        else:
                        #if 1 == 1:
                            val3 = ','.join(
                               "{} = EXCLUDED.{}".format(col, col) for col in column_names if col.replace('"','') not in identificador
                            )
                            SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT ({identificador}) DO UPDATE SET {val3}"





                    else:
                        val3 = ','.join(
                           "{} = EXCLUDED.{}".format(col, col) for col in column_names if col != f'"{identificador}"'
                        )
                        SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT ({identificador}) DO UPDATE SET {val3}"

                    #raise ValueError(val3)




                else:
                    SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT ({identificador}) DO NOTHING"

                if self.ignorar_if_error:
                    SQL_INSERT = f'''
                                        DO $$
                    BEGIN
                        {SQL_INSERT}  ; 

                    EXCEPTION
                        WHEN foreign_key_violation THEN
                            RAISE NOTICE 'Error: El registro de invoice_line_id no existe. Ignorando...';
                        WHEN others THEN
                            RAISE NOTICE 'Se produjo un error inesperado. Ignorando...';

                    END $$; '''

            if self.table == 'account_invoice_payment_rel':

                # SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) "

                # f"INSERT INTO account_move__account_payment (payment_id,invoice_id) VALUES (4 , SELECT id FROM  account_move WHERE x_invoice_id = 5 ) ;"

                SQL_INSERT = f'''
                                DO $$
            BEGIN
                INSERT INTO account_move__account_payment  (payment_id,invoice_id)  
                SELECT {fila[0]}, id  FROM account_move WHERE x_invoice_id = {fila[1]} ;

            EXCEPTION
                WHEN foreign_key_violation THEN
                    RAISE NOTICE 'Error: El registro de invoice_line_id no existe. Ignorando...';
                WHEN others THEN
                    RAISE NOTICE 'Se produjo un error inesperado. Ignorando...';

            END $$;
                                    '''


            if self.show_data:
                raise ValueError([SQL_INSERT,fila])

            #raise ValueError([SQL_INSERT,fila])
            self.env.cr.execute(SQL_INSERT, fila)
            #return


            '''
            try:
                self.env.cr.execute(SQL_INSERT, fila)
            except:
                raise ValueError([SQL_INSERT, fila])
                #raise ValueError([fila,SQL_INSERT])
                sql_strr = "SELECT * FROM product_template  "
                self.env.cr.execute(sql_strr)
                result = self.env.cr.fetchall()
                raise ValueError(result)
                raise ValueError([SQL_INSERT,fila,result])
            '''





            # raise ValueError(SQL_INSERT)

            # insert_query = sql.SQL(SQL_INSERT)
            # Ejecutar la instrucción
            # raise ValueError(SQL_INSERT)
            # cursor.execute(SQL_INSERT, fila)

        if self.table == 'account_invoice':
            return



        if not self.no_existe_id:
            sql_increment = f''' SELECT setval('public.{table}_id_seq', MAX(id)) FROM {table};'''
            self.env.cr.execute(sql_increment)


