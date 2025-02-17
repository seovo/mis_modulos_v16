from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
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

    log = fields.Text()
    #company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
    #                             default=lambda self: self.env.company)

    def show_lines(self):
        return {
            "name": f"LINEAS",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "migrate.model.jz",
            "target": "current",
            "domain": [('migrate_model_id','=',self.id)] ,
            "context": {
                'default_migrate_model_id': self.id
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


class MigrateModelColumnsJz(models.Model):
    _name  = 'migrate.model.columns.jz'
    name             = fields.Char(required=True)
    ignore           = fields.Boolean(string="Ignorar")
    type_field       = fields.Selection([('jsonb','jsonb')])
    migrate_model_id = fields.Many2one('migrate.model.jz')
    value_set        = fields.Text()


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
    #ignorar_if_error = fields.Boolean(string="Ignorar si Error")
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

            self.columns += self.env['migrate.model.columns.jz'].new(dx)

    def migrate_table(self):
        cursor = self.migrate_id.conect_postgres()

        select_columnsx = []
        column_names = []

        for colx in self.columns:
            #raise ValueError([col,col.ignore])
            if colx.ignore == True:
                continue
                #continue

            namm = colx.name



            column_names.append(namm)

            if colx.type_field in ['jsonb']:
                namm += '::text'
                #namm = f''' '"' || jsonb_to_json({namm}) || '"' AS {namm}_json '''
            if colx.value_set :
                namm = f'''{colx.value_set} '''
            select_columnsx.append(namm)
            if colx.ignore :
                raise ValueError([colx,colx.ignore,colx.name])


        #raise ValueError(select_columnsx)

        self._migrate_table(cursor, select_columnsx,column_names)



    def _migrate_table(self,cursor,select_columns,column_names):
        table = self.table
        string_columns = ",".join(select_columns)
        #quitar limit
        string_sql = f"SELECT {string_columns} FROM {table} "
        if table == 'res_users':
            add_where = f' AND {self.where_set}   ' if self.where_set else ''
            string_sql += f'  where id != {self.env.user.id} {add_where} ;'
        else:
            if self.where_set:
                string_sql += f'  where {self.where_set} ;'

        cursor.execute(string_sql)

        #try:
        #    cursor.execute(string_sql)
        #except:
        #    raise ValueError(string_sql)

        self.insert_record_migrate(cursor, table,column_names)
        #resultados = cursor.fetchall()


    def insert_record_migrate(self,cursor,table,column_names):

        if self.new_table:
            table = self.new_table

        resultados = cursor.fetchall()  # Obtener todos los resultados
        #raise ValueError(resultados)

        #raise ValueError(column_names)

        n = len(column_names)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('%s' for _ in range(n))

        # Generar la instrucción INSERT
        for fila in resultados:
            val1 = ','.join(column_names)
            val2 = corchetes_n
            # raise ValueError(val3)

            if self.no_existe_id:
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

            raise ValueError([SQL_INSERT,len(fila),fila])
            #self.env.cr.execute(SQL_INSERT, [fila[0],f'''"{fila[1]}"'''])


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