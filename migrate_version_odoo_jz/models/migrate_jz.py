from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql


class MigrateJz(models.Model):
    _name = 'migrate.jz'
    host = fields.Char(string="IP del Servidor Postgres",required=True)
    port = fields.Integer(string="Puerto Postgres",default=5432)
    dbname = fields.Char(string="Base de Datos Postgres",required=True)
    user   = fields.Char(string="Usuario Postgres",required=True)
    password = fields.Char(string="Contraseña Postgres",required=True)
    model_ids = fields.One2many('migrate.model.jz','migrate_id',string="Modelos")
    field_ids = fields.One2many('migrate.ir.model.fields','migrate_id',string="Modelos")

    log = fields.Text()
    from_version = fields.Integer()
    #company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
    #                             default=lambda self: self.env.company)

    #select A.id , A.name , B.model   from ir_model_fields as A join ir_model as B on  A.model_id = B.id ;
    @api.onchange('from_version')
    def set_fields(self):
        for record in self:
            host = self.host  # Cambia esto por la dirección de tu servidor
            port = self.port  # Puerto
            dbname = self.dbname  # Nombre de la base de datos
            user = self.user  # Tu usuario
            password = self.password  # Tu contraseña
            if host and port and dbname and user and password:
                cursor = record.conect_postgres()

                string_sql = f"select A.id , A.name , B.model   from ir_model_fields as A join ir_model as B on  A.model_id = B.id ; "
                try:
                    cursor.execute(string_sql)

                except:
                    return

                resultados = cursor.fetchall()

                for resultado in resultados:
                    dx = {
                            'id_sql': resultado[0],
                            'name': resultado[1],
                            'model': resultado[2],
                            'migrate_id': record._origin.id
                        }
                    try:
                        self.env['migrate.ir.model.fields'].create(dx)
                    except:
                        raise ValueError(dx)

                #raise ValueError(resultados)


    def add_modelos_usuales(self):
        #product_template
        #product_category
        #product_product
        #res_partner
        #sale_order
        #sale_order_line

        #account_move



        return


    def update_images(self):
        import requests
        import base64
        products = self.env['product.template'].search([('image_1920','=',False)],limit=100)

        for product in products:
            image_url = f"http://34.176.22.205:8069/web/image?model=product.template&id={product.id}&field=image"

            response = requests.get(image_url)
            if response.status_code == 200:
                # Guarda la imagen en el campo binario
                #content = response.content
                content =  base64.b64encode(response.content).decode('utf-8')
                #raise ValueError(content)
                product.image_1920 = content
            else:
                continue
                #raise ValueError(f"Error downloading image: {image_url}")

            #raise ValueError(url)



    def update_variant_combiation_products(self):

        line_variants_atrr =  self.env['product.template.attribute.line'].search([('value_count','=',False),('value_ids','!=',False)],limit=1000)
        line_variants_atrr._compute_value_count()
    def show_lines(self):
        return {
            "name": f"LINEAS",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "migrate.model.jz",
            "target": "current",
            "domain": [('migrate_id','=',self.id)] ,
            "context": {
                'default_migrate_id': self.id
            }
            #"res_id": self.id,
            #"view_id": view.id
        }


    def show_lot_availables(self):
        cursor = self.conect_postgres()
        self.migrate_users(cursor)

    def conect_postgres(self):

        host = self.host  # Cambia esto por la dirección de tu servidor
        port = self.port  # Puerto
        dbname = self.dbname  # Nombre de la base de datos
        user = self.user  # Tu usuario
        password = self.password  # Tu contraseña

        # Establecer conexión
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )

        # Crear un cursor

        cursor = connection.cursor()

        self.log = "ConexionExitosa"



        return cursor


class MigrateIrModelFields(models.Model):
    _name  = 'migrate.ir.model.fields'
    name = fields.Char(required=True)
    model = fields.Char(required=True)
    ir_model_fields_id = fields.Many2one('ir.model.fields',compute="get_ir_model_fields_id")
    migrate_id = fields.Many2one('migrate.jz',required=True)
    id_sql = fields.Integer()

    def get_ir_model_fields_id(self):
        for record in self:
            value = None
            model = self.env['ir.model.fields'].search([('name','=',record.name),('model_id.model','=',record.model)])
            if model:
                value = model.id
            record.ir_model_fields_id =  value


class MigrateModelColumnsJz(models.Model):
    _name  = 'migrate.model.columns.jz'
    name             = fields.Char(required=True)
    ignore           = fields.Boolean(string="Ignorar")
    type_field       = fields.Selection([('jsonb','jsonb')])
    migrate_model_id = fields.Many2one('migrate.model.jz')
    value_set        = fields.Text()
    is_field         = fields.Boolean(string="Es un Campo Odoo")

    #insert_as_jsonb   = fields.Boolean()


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
        for desc in cursor.description:
            #if desc[0] == 'name':
            #    raise ValueError(desc[1])
            dx = {
                'name': desc[0]
            }
            if desc[1] == 3802 :
                dx.update({'type_field':'jsonb'})

            #para version16 a version 17
            if table in ['product_template']:
                if desc[0] == 'message_main_attachment_id':
                    dx.update({'ignore': True})

            if table in ['product_product']:
                if desc[0] == 'message_main_attachment_id':
                    dx.update({'ignore': True})

            if table in ['res_partner']:
                if desc[0] == 'display_name':
                    dx.update({
                        'name': 'complete_name',
                        'value_set': 'display_name as complete_name'
                    })

                if desc[0] == 'message_main_attachment_id':
                    dx.update({'ignore': True})


            self.columns += self.env['migrate.model.columns.jz'].new(dx)

    def migrate_table(self):

        case_sql = None



        cursor = self.migrate_id.conect_postgres()

        select_columnsx = []
        column_names = []

        for colx in self.columns:
            #raise ValueError([col,col.ignore])
            if colx.ignore == True:
                continue
                #continue

            namm = f'"{colx.name}"'



            column_names.append(namm)

            if colx.type_field in ['jsonb']:
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
            if colx.ignore :
                raise ValueError([colx,colx.ignore,colx.name])


        #raise ValueError(select_columnsx)

        self._migrate_table(cursor, select_columnsx,column_names)



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
                string_sql += f'  where {self.where_set} ;'


        #raise ValueError(string_sql)

        cursor.execute(string_sql)

        #try:
        #    cursor.execute(string_sql)
        #except:
        #    raise ValueError(string_sql)


        if self.table == 'product_attribute_value_product_product_rel' and self.migrate_id.from_version <= 12:

            self.insert_product_variant_combination( cursor, table, column_names)


        else:
            self.insert_record_migrate(cursor, table, column_names)



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
        #raise ValueError(resultados)

        #raise ValueError(column_names)

        n = len(column_names)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('%s' for _ in range(n))

        # Generar la instrucción INSERT
        #raise ValueError(resultados)
        for fila in resultados:
            val1 = ','.join(column_names)
            val2 = corchetes_n
            # raise ValueError(val3)

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
                    val3 = ','.join(
                        "{} = EXCLUDED.{}".format(col, col) for col in column_names
                        if col != 'id'
                    )

                    SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT (id) DO UPDATE SET {val3}"
                else:
                    SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT (id) DO NOTHING"

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



            #raise ValueError([SQL_INSERT])
            self.env.cr.execute(SQL_INSERT, fila)


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



        if not self.no_existe_id:
            sql_increment = f''' SELECT setval('public.{table}_id_seq', MAX(id)) FROM {table};'''
            self.env.cr.execute(sql_increment)