from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql


# Si necesitas buscar por el nombre
selection_account_type_reverse = {
    "Receivable": "asset_receivable",
    "Bank and Cash": "asset_cash",
    "Current Assets": "asset_current",
    "Non-current Assets": "asset_non_current",
    "Prepayments": "asset_prepayments",
    "Fixed Assets": "asset_fixed",
    "Payable": "liability_payable",
    "Credit Card": "liability_credit_card",
    "Current Liabilities": "liability_current",
    "Non-current Liabilities": "liability_non_current",
    "Equity": "equity",
    "Current Year Earnings": "equity_unaffected",
    "Income": "income",
    "Other Income": "income_other",
    "Expenses": "expense",
    "Depreciation": "expense_depreciation",
    "Cost of Revenue": "expense_direct_cost",
    "Off-Balance Sheet": "off_balance",
}


#id < ( %LAST +%NUM_RECORDS ) AND id >= %LAST

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
    create_record_master = fields.Boolean(string='Crear Registros Maestros')

    is_part_cron = fields.Boolean(string='Ejecutar por Lotes Cron')
    last_value = fields.Integer(string='Ultimo Registro Ejecutado %LAST')
    records_value = fields.Integer(string="Numero de Registros %NUM_RECORDS ",default=200)

    @api.onchange('is_part_cron')
    def change_is_part_cron(self):
        if not self.where_set :
            self.where_set = 'id < ( %LAST +%NUM_RECORDS ) AND id >= %LAST'

            if self.table == 'account_invoice_line':
                self.where_set = f'''
                id < ( %LAST +%NUM_RECORDS ) AND id >= %LAST 
                AND  invoice_id  NOT IN (SELECT id FROM account_invoice  WHERE move_id IS NULL)
                AND display_type IS NULL  ;
                '''

            if self.table == 'account_invoice':
                self.where_set = 'move_id < ( %LAST +%NUM_RECORDS ) AND move_id >= %LAST and move_id IS NOT NULL ;'

    def validate_table(self):

        if self.table in self.migrate_id.get_modelos_old():

            self.new_table = self.migrate_id.convert_modelos_old(self.table)



        table_model = self.new_table or self.table


        table_model = table_model.replace('_', '.')

        model_object = self.env['ir.model'].search([('model', '=',table_model)])

        if model_object:
            self.model_id = model_object.id




        if self.table == 'account_invoice_line':
            self.identificador = 'name , invoice_id'
            self.update_if_exist = True
        if self.table in ['account_tax', 'res_currency']:
            self.where_set = "active = 't' ; "

        if self.table == 'account_account':
            self.where_set = '''

            id IN (  SELECT DISTINCT aml.account_id  FROM account_move_line aml )

            '''

        if self.table == 'account_invoice':
            self.where_set = 'move_id IS NOT NULL ;'

    def validate_columns_no_existentes(self,table=None):
        if not table:
            table = self.table

        list_field_insert = []
        for columnx in self.columns:
            if columnx.ignore == True:
                continue
            list_field_insert.append(columnx.name)

        id_origin = self.id if type(self.id) == int else self._origin.id

        if table == 'account_payment':
            if 'company_id' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'company_id' ,
                    'value_set': f"{self.env.company.id}",
                    'migrate_model_id': id_origin,
                })

            if 'date' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'date' ,
                    'value_set': '"payment_date" as date',
                    'migrate_model_id': id_origin,
                })

        if table == 'res_partner':
            if 'autopost_bills' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'autopost_bills' ,
                    'value_set': "'ask'",
                    'migrate_model_id': id_origin,
                })

        if table == 'product_template':
            if 'service_tracking' not in  list_field_insert:
                self.env['migrate.model.columns.jz'].create({
                    'name': 'service_tracking' ,
                    'value_set': "'no'",
                    'migrate_model_id': id_origin,
                })

        if table == 'account_move_line':
            if self.migrate_id.current_version >= 13:
                if 'display_type' not in list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'display_type',
                        'value_set': '''CASE
         WHEN product_id IS NOT NULL THEN 'product' 
ELSE   'tax'
END AS display_type      ''',
                        'migrate_model_id': id_origin,
                    })

                if 'x_invoice_id' not in list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'x_invoice_id',
                        'value_set': "invoice_id",
                        'migrate_model_id': id_origin,
                    })

        if table == 'account_move':
            if self.migrate_id.current_version > 15:
                #esto es odoo18 	reverse_entry_id
                if 'reversed_entry_id' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'reversed_entry_id',
                        'value_set': ' "reverse_entry_id" as reversed_entry_id    ',
                        'migrate_model_id': id_origin,
                    })
                if 'move_type' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'move_type',
                        'value_set': "'entry'",
                        'migrate_model_id': id_origin,
                    })
                if 'auto_post' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'auto_post',
                        'value_set': "'no'",
                        'migrate_model_id': id_origin,
                    })

        if table == 'account_invoice':
            if self.migrate_id.current_version > 12:
                if 'x_invoice_id' not in list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'x_invoice_id',
                        'value_set': 'id',
                        'migrate_model_id': id_origin,
                    })

                if 'move_type' not in list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'move_type',
                        'value_set': 'type',
                        'migrate_model_id': id_origin,
                    })

                if 'auto_post' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'auto_post',
                        'value_set': "'no'",
                        'migrate_model_id': id_origin,
                    })

                if 'invoice_date' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'invoice_date',
                        'value_set': "date_invoice",
                        'migrate_model_id': id_origin,
                    })

                if 'invoice_date_due' not in  list_field_insert:
                    self.env['migrate.model.columns.jz'].create({
                        'name': 'invoice_date_due',
                        'value_set': 'date_due',
                        'migrate_model_id': id_origin,
                    })

    @api.onchange('table')
    def change_table(self):
        self.validate_table()
        table =  self.table


        cursor = self.migrate_id.conect_postgres()

        string_sql = f"SELECT * FROM {table} LIMIT 1"
        #raise ValueError(string_sql)
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



        for desc in cursor.description:

            #if desc[0] == 'description_sale':
            #    raise ValueError(desc[1])

            #raise ValueError(type(self.id))

            id_self = self.id



            if type(id_self) != int :
                id_model = self._origin.model_id.id
                id_self = self._origin.id
            else:
                id_model = self.model_id.id




            dx = {
                'migrate_model_id' :  id_self ,
                'name': desc[0] ,
                'ignore': False ,
                'type_field_postgres': desc[1]
            }



            exist_field_odoo = self.env['ir.model.fields'].search([
                ('model_id','=',id_model),('name','=',desc[0]),('store','=',True)
            ])


            if self.model_id:
                if not exist_field_odoo:
                    dx.update({'ignore': True})
                else:
                    dx.update({'ir_model_field_id': exist_field_odoo.id })
                    # tipo JSON A TEXTO , porque mi insercion solo acepto texto
                    if desc[1] == 3802:
                        dx.update({'type_field': 'jsonb_text'})

                    # TIPO TEXTO A JSONB 1043 = varchar
                    if desc[1] in [1043, 25] and exist_field_odoo.translate:
                        dx.update({'type_field': 'text_jsonb'})

                    if (desc[1] in [1043,25] and exist_field_odoo.translate
                            and table in self.migrate_id.get_tables_maestros()):
                        dx.update({'type_field': False})



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

            if table in ['account_invoice']:
                if desc[0] in ['id']:
                    dx.update({
                        'value_set': 'move_id'
                    })

                if desc[0] in ['state']:
                    dx.update({
                        'value_set': f'''
                        CASE
                          WHEN state = 'cancel' THEN  'cancel'
                          WHEN state = 'annul' THEN  'cancel'
                          WHEN state = 'draft' THEN 'draft'
                          ELSE 'posted' 
                        END AS state
                        '''
                    })


            #raise ValueError(dx)

            try:
                self.env['migrate.model.columns.jz'].create(dx)
            except:
                raise ValueError(dx)


        self.validate_columns_no_existentes(table)

    def remplace_fields(self):

        self.migrate_id.generate_text_set_clave()

        #raise ValidationError('oke')
        # para los campos que son journal_id
        account_fields = self.env['migrate.model.columns.jz'].search([
            ('name', '=', 'group_id'), ('migrate_model_id', '=', self.id),('migrate_model_id.table','=','account_account')
        ])
        if account_fields:
            for jfiels in account_fields:
                jfiels.value_set = self.migrate_id.text_account_group


        jurnal_fields = self.env['migrate.model.columns.jz'].search([
            ('name', '=', 'journal_id'),('migrate_model_id','=',self.id)
        ])

        if jurnal_fields:
            for jfiels in jurnal_fields:
                jfiels.value_set = self.migrate_id.text_journal

        currency_fields = self.env['migrate.model.columns.jz'].search([
            ('name', 'in', ['currency_id','company_currency_id']),('migrate_model_id','=',self.id)
        ])

        if currency_fields:
            for jfiels in currency_fields:
                text_reemplaze = self.migrate_id.text_currency
                text_reemplaze = text_reemplaze.replace('currency_id',jfiels.name)
                jfiels.value_set = text_reemplaze

        act_fields = self.env['migrate.model.columns.jz'].search(
            [('name', '=', 'user_type_id'), ('migrate_model_id', '=', self.id)])

        if act_fields:
            for jfiels in act_fields:
                jfiels.value_set = self.migrate_id.text_account_type

        tax_group_fields = self.env['migrate.model.columns.jz'].search(
            [('name', '=', 'tax_group_id'), ('migrate_model_id', '=', self.id)])

        if tax_group_fields:
            for jfiels in tax_group_fields:
                jfiels.value_set = self.migrate_id.text_tax_group

        tax_fields = self.env['migrate.model.columns.jz'].search([('name', '=',['tax_line_id','account_tax_id'] ),('migrate_model_id','=',self.id)])


        if tax_fields:
            for jfiels in tax_fields:
                text_reemplaze = self.migrate_id.text_tax
                text_reemplaze = text_reemplaze.replace('account_tax_id',jfiels.name)
                jfiels.value_set = text_reemplaze


        tax_fields2 = self.env['migrate.model.columns.jz'].search([
            ('name', '=', 'tax_id'),('migrate_model_id','=',self.id)
        ])

        if tax_fields2:
            for jfiels2 in tax_fields2:

                text_tax = self.migrate_id.text_tax

                if text_tax:
                    text_tax = text_tax.replace('account_tax_id', 'tax_id')
                    jfiels2.value_set = text_tax

        account_fields = self.env['migrate.model.columns.jz'].search([
            ('name', 'in', [
                'account_id','profit_account_id','loss_account_id','bank_account_id',
                'default_credit_account_id','default_debit_account_id',
                'debit_move_id','credit_move_id'
            ]),
            ('migrate_model_id','=',self.id)])

        if account_fields:
            for jfiels in account_fields:
                text_account = self.migrate_id.text_account
                text_account = text_account.replace('account_id',jfiels.name)
                jfiels.value_set = text_account

        location_fields = self.env['migrate.model.columns.jz'].search([('name', '=', 'location_id'),('migrate_model_id','=',self.id)])

        if location_fields:
            for jfiels in location_fields:
                jfiels.value_set = self.migrate_id.text_location

        country_fields = self.env['migrate.model.columns.jz'].search([('name', '=', 'country_id'),('migrate_model_id','=',self.id)])

        if country_fields:
            for jfiels in country_fields:
                jfiels.value_set = self.migrate_id.text_country

        state_fields = self.env['migrate.model.columns.jz'].search([('name', '=', 'state_id'),('migrate_model_id','=',self.id)])

        if state_fields:
            for jfiels in state_fields:
                jfiels.value_set = self.migrate_id.text_state

        pricelist_fields = self.env['migrate.model.columns.jz'].search(
            [('name', '=', 'pricelist_id'), ('migrate_model_id', '=', self.id)]
        )

        if pricelist_fields:
            for jfiels in pricelist_fields:
                jfiels.value_set = self.migrate_id.text_pricelist

        state_payment = self.env['migrate.model.columns.jz'].search(
            [('name', '=', 'state'), ('migrate_model_id', '=', self.id),('migrate_model_id.table','=','account_payment')])

        if state_payment:
            state_payment.value_set = f'''
            CASE
               WHEN state = 'posted'  THEN  'paid'
               WHEN state = 'cancelled'  THEN  'canceled'
            ELSE state
            END AS state
            '''
            for jfiels in state_fields:
                jfiels.value_set = self.migrate_id.text_state

    def migrate_table(self):

        self.validate_columns_no_existentes()
        self.remplace_fields()

        case_sql = None

        cursor = self.migrate_id.conect_postgres()
        table = self.new_table or self.table


        #ESTO NO SE ESTA USANDO
        '''
        if ',' in self.identificador :


            name_constraint = 'TEMPORAL_'+table

            queryy = f"""
                ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name_constraint};
                ALTER TABLE  {table}
                ADD CONSTRAINT {name_constraint}
                UNIQUE  ({self.identificador});
            """
            #self.env.cr.execute(queryy)   
        '''

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

            if colx.type_field in ['text_jsonb'] and colx.type_field_postgres in [1043,25]:
                # code_pais = self.company.country_id.
                # namm += '::jsonb'
                # esto es para cuando el texto vine como json b aunque sea tipo texto por verificar si viene un caso asi
                # namm = f'''
                # CASE
                #   WHEN {namm} IS NOT NULL AND jsonb_typeof({namm}::jsonb) IS NOT NULL THEN {namm}::text
                #   ELSE jsonb_build_object('en_US', COALESCE({namm}, ''))::text
                # END AS {namm}
                # '''

                namm = f'''
                jsonb_build_object(
                    'en_US', {colx.name}
                )::text AS {namm}
                '''
                #,'es_PE', {colx.name}


            #todos los  que son company_dependent  tendran esta estructura debe ser automatico ahorita est manual

            if colx.ir_model_field_id and colx.ir_model_field_id.company_dependent == True:
                namm = f'''
                     jsonb_build_object(
                        '1', {colx.name}
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

        #string_sql = f'SELECT service_to_purchase FROM {table}'

        #resultados = cursor.fetchall()
        #raise ValueError(resultados)



        cursor.execute(string_sql)
        resultados = cursor.fetchall()

        if not resultados or len(resultados) == 0:
            self.last_value = 0
            return

        #raise ValueError([string_sql,resultados[0]])

        #try:
        #    cursor.execute(string_sql)
        #except:
        #    raise ValueError(string_sql)

        #version 12

        if self.migrate_id.from_version == 12:
            if self.table == 'product_attribute_value_product_product_rel':
                self.insert_product_variant_combination( cursor, resultados)
            else:
                self.insert_record_migrate(cursor, table, column_names,resultados=resultados)
        else:
            self.insert_record_migrate(cursor, table, column_names,resultados=resultados)

        if  self.where_set and '%LAST' in self.where_set:
            self.last_value = self.last_value + self.records_value



        #resultados = cursor.fetchall()

    def insert_product_variant_combination(self, cursor , resultados):

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

    def insert_record_migrate(self,cursor,table,column_names,resultados=None):

        if self.new_table:
            table = self.new_table

        #column_names = [f'"{element}"' for element in column_names]

        if not resultados:
            resultados = cursor.fetchall()  # Obtener todos los resultados

        #if self.show_data:
        #    raise ValueError(resultados)

        if self.table == 'account_group':
            position_name = column_names.index('"name"')
            position_parent_id = column_names.index('"parent_id"')
            position_code_prefix = column_names.index('"code_prefix"')


            for agroup in resultados:
                value_name = agroup[position_name]
                value_parent_id = agroup[position_parent_id]
                value_code_prefix = agroup[position_code_prefix]

                agroup_migration = self.env['account.group.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', agroup[0])
                ])

                data_insert = {
                    'id_sql': agroup[0],
                    'name': value_name,
                    'migrate_id': self.migrate_id.id ,
                    'parent_id': value_parent_id ,
                    'code': value_code_prefix
                }

                exist_account_group = self.env['account.group'].search([
                    '|',('code_prefix_end','=',value_code_prefix),('code_prefix_start','=',value_code_prefix)
                ])

                if exist_account_group:
                    data_insert.update({
                        'account_group_id': exist_account_group.id
                    })

                if not agroup_migration:
                    agroup_migration.create(data_insert)
                else:
                    agroup_migration.write(data_insert)
            return


        if self.table == 'account_account_type':
            for atype in resultados:
                atype_migration = self.env['account.type.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', atype[0])
                ])

                data_insert = {
                    'id_sql' : atype[0] ,
                    'name': atype[1] ,
                    'migrate_id' : self.migrate_id.id
                }

                try:
                    selection_account_type = selection_account_type_reverse[atype[1]]
                    data_insert.update({
                        'account_type': selection_account_type
                    })
                except:
                    pass



                if not atype_migration:
                    atype_migration = self.env['account.type.migration.jz'].create(data_insert)
                else:
                    atype_migration.write(data_insert)






            return


        if self.table == 'account_tax_group':
            for taxgroup in resultados:

                name_group = taxgroup[1]

                dom = [
                    ('name', 'ilike', name_group),('country_id','=',self.env.company.country_id.id)
                ]

                exist_tax_group = self.env['account.tax.group'].search(dom)

                #if len(exist_tax_group) > 1:
                #    raise ValidationError(dom)

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'id_sql': taxgroup[0] ,
                    'name':  name_group

                }

                if exist_tax_group and len(exist_tax_group) == 1:
                    data_insert.update({
                        'tax_group_id': exist_tax_group.id
                    })

                journal_migration = self.env['tax.group.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', taxgroup[0])
                ])

                if not journal_migration:
                    journal_migration = self.env['tax.group.migration.jz'].create(data_insert)

            return


        if self.table == 'product_pricelist':
            for pricelist in resultados:
                id_pricelist = int(pricelist[0])
                name_pricelist = str(pricelist[1])
                pricelist_migration = self.env['pricelist.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', id_pricelist )
                ])

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': name_pricelist,
                    'id_sql': id_pricelist
                }

                if not  pricelist_migration:
                    self.env['pricelist.migration.jz'].create(data_insert)



            return

        if self.table == 'account_journal':
            if self.create_record_master:
                position_code = column_names.index('"code"')
                position_type = column_names.index('"type"')
                position_account_debit = column_names.index('"default_debit_account_id"')
                position_account_credit = column_names.index('"default_credit_account_id"')
                position_currency_id = column_names.index('"currency_id"')
                position_profit_account_id  = column_names.index('"profit_account_id"')
                position_loss_account_id = column_names.index('"loss_account_id"')
                position_bank_account_id = column_names.index('"bank_account_id"')
                position_bank_statements_source = column_names.index('"bank_statements_source"')
                position_show_on_dashboard = column_names.index('"show_on_dashboard"')
                position_payment_form = column_names.index('"payment_form"')

            #raise ValidationError(str(resultados))
            for journal in resultados:
                # raise ValueError(journal)
                dom = [
                        ('migrate_id', '=', self.migrate_id.id),
                        ('id_sql', '=', int(journal[0]))
                    ]
                try:
                    journal_migration = self.env['journal.migration.jz'].search(dom)
                except:
                    raise ValidationError(str(dom))



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

                if not exist_diario and self.create_record_master:

                    value_code = journal[position_code]
                    value_type = journal[position_type]
                    value_account_debit = journal[position_account_debit]
                    value_currency_id = journal[position_currency_id]
                    value_profit_account_id = journal[position_profit_account_id]
                    value_loss_account_id = journal[position_loss_account_id]
                    value_bank_account_id = journal[position_bank_account_id]
                    value_bank_statements_source = journal[position_bank_statements_source]

                    value_payment_form = journal[position_payment_form]

                    #if not value_account_debit:
                    #    raise ValidationError(name_journal)




                    dict_create_journal = {
                        'name': name_journal ,
                        'code': value_code ,
                        'type': value_type ,
                        'default_account_id': value_account_debit ,
                        'currency_id': value_currency_id ,
                        'company_id': self.env.company.id ,
                        'profit_account_id': value_profit_account_id ,
                        'loss_account_id': value_loss_account_id ,
                        'bank_account_id': value_bank_account_id ,
                        'bank_statements_source': value_bank_statements_source ,

                        'payment_form': value_payment_form ,


                    }

                    if value_code == 'TDCIP':
                        raise ValidationError(str(dict_create_journal))

                    #if value_code == 'bank':
                    #    value_account_credit = journal[position_account_credit]
                    #    dict_create_journal.write({
                    #        'suspense_account_id': value_account_credit ,

                    #    })

                    #exist_diario = self.env['account.journal'].create(dict_create_journal)
                    #'''
                    try:
                        exist_diario = self.env['account.journal'].create(dict_create_journal)
                    except:
                        exist_diario = self.env['account.journal'].search(['code','=',value_code])
                        #exist_diario = None
                        raise ValidationError(str([dict_create_journal,exist_diario]))
                    #'''


                if exist_diario:
                    data_insert.update({
                        'journal_id'  : exist_diario.id
                    })

                if not journal_migration:
                    self.env['journal.migration.jz'].create(data_insert)
                else:
                    journal_migration.write(data_insert)


            return

        if self.table == 'res_currency':

            for currency in resultados:
                # raise ValueError(journal)

                name_currency = str(currency[1])
                id_currency = int(currency[0])

                exist_currency = self.env['res.currency'].search([('name', '=', name_currency)])

                currency_migration = self.env['currency.migration.jz'].search([('id_sql', '=', id_currency)])

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': name_currency,
                    'id_sql': id_currency
                    # 'journal_id':
                }

                if exist_currency:
                    data_insert.update({
                        'currency_id': exist_currency.id
                    })

                if currency_migration:
                    currency_migration.write(data_insert)
                else:
                    currency_migration = self.env['currency.migration.jz'].create(data_insert)

            return


        if self.table == 'account_tax':
            #raise ValueError(column_names)
            position_description  = column_names.index('"description"')
            position_type_tax_use = column_names.index('"type_tax_use"')
            position_amount       = column_names.index('"amount"')
            position_name         = column_names.index('"name"')
            position_include_base_amount = column_names.index('"include_base_amount"')


            if self.create_record_master:
                position_amount_type  = column_names.index('"amount_type"')
                position_price_include = column_names.index('"price_include"')
                position_analytic = column_names.index('"analytic"')
                position_tax_exigibility = column_names.index('"tax_exigibility"')
                position_account_id = column_names.index('"account_id"')
                position_tax_group_id = column_names.index('"tax_group_id"')
                position_refund_account_id =  column_names.index('"refund_account_id"')

            #raise ValueError(resultados[0][position_description])



            if self.create_record_master:
                for result_tax in resultados:
                    tax_migration = self.env['tax.migration.jz'].search([
                        ('migrate_id', '=', self.migrate_id.id),
                        ('id_sql', '=', int(result_tax[0]))
                    ])
                    if tax_migration:

                        if not tax_migration.tax_id:

                            value_description = result_tax[position_description]
                            value_type_tax_use = result_tax[position_type_tax_use]
                            value_amount = result_tax[position_amount]
                            value_name = result_tax[position_name]

                            value_amount_type = result_tax[position_amount_type]
                            value_price_include = result_tax[position_price_include]
                            value_include_base_amount = result_tax[position_include_base_amount]
                            value_analytic = result_tax[position_analytic]
                            value_tax_exigibility = result_tax[position_tax_exigibility]
                            value_account_id = result_tax[position_account_id]
                            value_tax_group_id = result_tax[position_tax_group_id]
                            value_refund_account_id = result_tax[position_refund_account_id]

                            #if value_name == 'Retención 2% ISR por Transferencia de Títulos':
                            #    raise ValueError(tax_migration.tax_id)

                            data_tax = {
                                'name': value_name,
                                'type_tax_use': value_type_tax_use,
                                'amount_type': value_amount_type,
                                'amount': value_amount,
                                'description': value_description or value_name,
                                'invoice_label': value_name ,
                                'include_base_amount': value_include_base_amount,
                                'analytic': value_analytic,
                                'tax_exigibility': value_tax_exigibility,
                                'tax_group_id': value_tax_group_id

                            }

                            if value_price_include and value_price_include == True:
                                data_tax.update({
                                    'price_include_override': 'tax_included'
                                })

                            # raise ValueError([column_names, data_tax])

                            exist_tax = self.env['account.tax'].create(data_tax)
                            tax_migration.tax_id = exist_tax.id

                            if value_account_id:
                                for repartition_line in exist_tax.invoice_repartition_line_ids:
                                    if repartition_line.repartition_type == 'tax':
                                        repartition_line.account_id = value_account_id

                                # raise ValidationError(exist_tax.invoice_repartition_line_ids)

                            if value_refund_account_id:
                                for refun_repartition_line in exist_tax.refund_repartition_line_ids:
                                    if refun_repartition_line.repartition_type == 'tax':
                                        refun_repartition_line.account_id = value_refund_account_id

                            # raise ValueError([column_names, result_tax])
                return


            tax_use_ids = []
            for result_tax in resultados:
                # REALIZAR LA MIGRACION AQUI
                # raise ValueError(journal)
                value_description = result_tax[position_description]
                value_type_tax_use = result_tax[position_type_tax_use]
                value_amount = result_tax[position_amount]
                value_name = result_tax[position_name]

                # VALIDACION NOMBRE
                dominio_tax = [
                    ('type_tax_use', '=', value_type_tax_use),
                    ('amount', '=', value_amount),
                    ('name', 'ilike', value_name),
                    '|', ('active', '=', True), ('active', '=', False)

                ]
                exist_tax = self.env['account.tax'].search(dominio_tax)

                if value_name == '9% ITBIS Comprasa' :
                    raise ValueError(exist_tax)

                if len(exist_tax) > 1:
                    exist_tax = None

                #VALIDAR NOMBRE Y DESCRIPCION
                dominio_tax = [
                    ('type_tax_use', '=', value_type_tax_use),
                    ('amount', '=', value_amount),
                    ('name', '=', value_name),
                    #('description', 'ilike', value_description),
                    '|', ('active', '=', True), ('active', '=', False)

                ]
                exist_tax = self.env['account.tax'].search(dominio_tax)

                #if value_name == '9% ITBIS Compras' :
                #    raise ValueError(exist_tax)

                if len(exist_tax) > 1:
                    exist_tax = None


                if not exist_tax:
                    # VALIDACION DESCRIPCION->NOMBRE , MONTO , NOMBRE -> DESCRIPCION ,  E IMPUESTO
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        ('description', 'ilike', value_name),
                        ('name', 'ilike', value_description),
                        '|', ('active', '=', True), ('active', '=', False)

                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    if len(exist_tax) > 1:
                        exist_tax = None



                # VALIDACION DESCRIPCION->NOMBRE , MONTO  E IMPUESTO
                if not exist_tax:
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        ('description', 'ilike', value_name),
                        '|', ('active', '=', True), ('active', '=', False)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    if len(exist_tax) > 1:
                        exist_tax = None


                #VALIDACION NOMBRE -> DESCRIPCION , ,MONTO E IMPUESTO
                if not exist_tax:
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        ('name', 'ilike', value_description),
                        '|', ('active', '=', True), ('active', '=', False)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    if exist_tax and len(exist_tax) > 1:
                        exist_tax = None

                    if exist_tax and exist_tax.id in tax_use_ids:
                        exist_tax = None



                #VALIDACION DESCRIPCION
                if not exist_tax:
                    # VALIDACION DESCRIPCION / NOMBRE E IMPUESTO
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('description', 'ilike', value_name),
                        '|', ('active', '=', True), ('active', '=', False)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    if len(exist_tax) > 1:
                        exist_tax = None

                #if value_name == 'Retención a Proveedores Informales de Bienes (75%)':
                #    raise ValueError([exist_tax,tax_use_ids,dominio_tax])


                #VALIDACION PORCENTAJE

                if not exist_tax:
                    # Validacion solo por porcentaje

                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        '|', ('active', '=', True), ('active', '=', False)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    # if value_description == '2% ISC':
                    #    raise V

                    if len(exist_tax) > 1:
                        exist_tax = None

                #if value_name == '18% ITBIS Compras':
                #    raise ValueError([exist_tax,tax_use_ids])

                if exist_tax and  exist_tax.id in tax_use_ids:
                    exist_tax = None

                if exist_tax:
                    tax_use_ids.append(exist_tax.id)

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': value_name,
                    'id_sql': int(result_tax[0]),
                    'type': value_type_tax_use ,
                    'amount': value_amount ,
                    'tax_id': exist_tax.id if exist_tax else None
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

                tax_migration = self.env['tax.migration.jz'].search([
                    ('migrate_id', '=', self.migrate_id.id),
                    ('id_sql', '=', int(result_tax[0]))
                ])

                if tax_migration.tax_id:
                    continue


                value_description = result_tax[position_description]
                value_type_tax_use = result_tax[position_type_tax_use]
                value_amount = result_tax[position_amount]
                value_name = result_tax[position_name]

                dominio_tax = [
                    ('type_tax_use', '=', value_type_tax_use),
                    ('amount', '=', value_amount),
                    ('name', 'ilike', value_name),
                    '|', ('active', '=', True), ('active', '=', False)

                ]
                exist_tax = self.env['account.tax'].search(dominio_tax)

                if len(exist_tax) > 1:
                    exist_tax = None

                if not exist_tax:
                    # VALIDACION NAME->DESCRIPCION / NOMBRE E IMPUESTO
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        ('tax_migration_jz_ids', '=', False),
                        ('description', 'ilike', value_name),
                        # ('id','not in',tax_use_ids)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                    # if value_name == 'Retención 2% ISR por Transferencia de Títulos':
                    #    raise ValueError([exist_tax,tax_use_ids,dominio_tax])

                    if len(exist_tax) > 1:
                        exist_tax = None

                    if exist_tax in tax_use_ids:
                        exist_tax = None





                #DESCRIPTION -> NAME
                if not exist_tax:
                    dominio_tax = [
                        ('type_tax_use', '=', value_type_tax_use),
                        ('amount', '=', value_amount),
                        ('tax_migration_jz_ids', '=', False),
                        ('name', 'ilike', value_description),
                        # ('id','not in',tax_use_ids)
                    ]

                    exist_tax = self.env['account.tax'].search(dominio_tax)

                if len(exist_tax) > 1:
                    exist_tax = None

                if exist_tax in tax_use_ids:
                    exist_tax = None


                #if value_name == 'Retención 2% ISR a Física (con Materiales)':
                #    raise ValueError(exist_tax)

                if exist_tax:
                    tax_use_ids.append(exist_tax.id)
                    tax_migration.write({'tax_id': exist_tax.id })






            return

        if self.table == 'account_account':
            position_name = column_names.index('"name"')
            position_code = column_names.index('"code"')

            if self.create_record_master:
                position_deprecated = column_names.index('"deprecated"')
                position_note  = column_names.index('"note"')
                position_group_id = column_names.index('"group_id"')
                position_reconcile = column_names.index('"reconcile"')

            for account in resultados:
                id_account = int(account[0])
                name_account = str(account[position_name])
                code_account = str(account[position_code])


                exist_account = self.env['account.account'].search([('code', '=', code_account)])

                data_insert = {
                    'migrate_id': self.migrate_id.id,
                    'name': name_account,
                    'id_sql': id_account,
                    'code': code_account ,

                }

                if exist_account:
                    data_insert.update({
                        'account_id': exist_account.id
                    })
                else:
                    if self.create_record_master:
                        value_deprecated = account[position_deprecated]
                        value_note = account[position_note]
                        value_group = account[position_group_id]
                        value_reconcile = account[position_reconcile]
                        if not code_account or code_account == 'False':
                            raise ValidationError(str([name_account,id_account]))
                        data_create_account = {
                            'company_ids': [(6, 0, [self.env.company.id])] ,
                            'name': name_account ,
                            'code': code_account ,
                            'deprecated': value_deprecated ,
                            'note': value_note ,
                            'group_id': value_group ,
                            'reconcile': value_reconcile

                        }

                        try:
                            exist_account = self.env['account.account'].create(data_create_account)
                        except:
                            raise ValidationError(str(data_create_account))



                        data_insert.update({
                            'account_id': exist_account.id
                        })


                account_migration = self.env['account.migration.jz'].search([
                    ('id_sql', '=', id_account)
                ])
                if account_migration:
                    account_migration.write(data_insert)
                else:
                    self.env['account.migration.jz'].create(data_insert)

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

        if self.new_table == 'account_move_line' and self.table == 'account_invoice_line':
            position_invoice_id = column_names.index('"invoice_id"')
            position_name = column_names.index('"name"')
            position_price_unit  = column_names.index('"price_unit"')
            position_quantity  = column_names.index('"quantity"')
            for fila in resultados:
                value_invoice_id = fila[position_invoice_id]
                value_name = fila[position_name]
                value_price_unit = fila[position_price_unit]
                value_quantity = fila[position_quantity]

                values_select = []

                #BUSCAR DESCRIPCION Y PRODUCTO
                SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND name = %s AND product_id IS NOT NULL "

                self.env.cr.execute(SQL_CONSULTA, [value_invoice_id, value_name])
                result = self.env.cr.fetchall()

                if len(result) == 0:
                    #BUSCAR SOLO NOMBRE
                    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s AND name = %s "

                    self.env.cr.execute(SQL_CONSULTA, [value_invoice_id, value_name])
                    result = self.env.cr.fetchall()

                if len(result) > 1:
                    #BUSCAR POR CREDITO
                    SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s  AND name = %s  AND ( credit = %s OR debit = %s)"

                    values_select = [value_invoice_id,  value_name , value_price_unit , value_price_unit]

                    self.env.cr.execute(SQL_CONSULTA, values_select)
                    result = self.env.cr.fetchall()

                    if len(result) == 0:
                        # BUSCAR SOLO NOMBRE
                        SQL_CONSULTA = f"SELECT  id FROM  {table} WHERE  x_invoice_id = %s  AND name = %s  AND quantity = %s "

                        values_select =  [value_invoice_id, value_name , value_quantity]

                        self.env.cr.execute(SQL_CONSULTA,values_select )
                        result = self.env.cr.fetchall()


                if len(result) == 1:
                    SQL_INSERT = f'''
                    UPDATE {table} SET  price_unit = %s , display_type = 'product' WHERE  id = %s '''

                    self.env.cr.execute(SQL_INSERT, [value_price_unit, result[0] ])
                else:
                    raise ValidationError(str([result,fila,SQL_CONSULTA,values_select]))

                #raise ValidationError(str(result))

            return



        if self.last_value <= 0 :
            if self.table == 'product_taxes_rel':
                self.env.cr.execute("TRUNCATE TABLE product_taxes_rel ;")

            if self.table == 'product_supplier_taxes_rel':
                self.env.cr.execute("TRUNCATE TABLE product_supplier_taxes_rel ;")

            if self.table == 'account_tax_purchase_order_line_rel':
                self.env.cr.execute("TRUNCATE TABLE account_tax_purchase_order_line_rel ;")

            if self.table == 'account_move_line_account_tax_rel':
                self.env.cr.execute("TRUNCATE TABLE account_move_line_account_tax_rel ;")

            if self.table == 'account_move_line':
                sql = '''
                WITH sub AS (
    SELECT
        aml.id,
        CASE
            -- Case 1: Not an invoice -> Product
            WHEN am.move_type NOT IN
            ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
            THEN 'product'
            -- Case 2: It's a tax line -> Tax
            WHEN aml.tax_line_id IS NOT NULL THEN 'tax'
            -- Case 3: It's a Receivable or Payable account -> Payment Term
            WHEN aa.account_type IN
            ('asset_receivable', 'liability_payable') THEN 'payment_term'
            -- Case 4: Everything else -> Product
            ELSE 'product'
        END AS display_type
    FROM account_move_line AS aml
    LEFT JOIN account_move AS am ON am.id = aml.move_id
    LEFT JOIN account_account AS aa ON aa.id = aml.account_id
    WHERE aml.display_type IS NULL AND am.id = aml.move_id
)
UPDATE account_move_line AS aml
   SET display_type = sub.display_type
FROM sub
WHERE aml.id = sub.id;
                '''



                sql = '''
                
                UPDATE account_move_line AS aml 
                   SET display_type = 'product'
                WHERE move_id IN (
                     SELECT id 
                     FROM account_move 
                     WHERE move_type = 'entry'
                ) ;
                
                '''

                #sql = 'UPDATE account_move SET amount_total_in_currency_signed = 0'

                #raise ValidationError(sql)
                #raise ValidationError([self.table, self.last_value])
                self.env.cr.execute(sql)




        #raise ValueError(column_names)

        n = len(column_names)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('%s' for _ in range(n))

        identificador = self.identificador

        # Generar la instrucción INSERT

        contador = 0

        for fila in resultados:
            val1 = ','.join(column_names)
            val2 = corchetes_n





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

            #contador += 1

            #if type(fila[31]) != bool :
            #    raise ValueError(fila)

            #if str(fila[31]) != 'false' :
            #    raise ValueError([fila,contador])

            #raise ValueError(fila[31])

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


