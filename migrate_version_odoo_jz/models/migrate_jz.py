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

    def show_lot_availables(self):
        cursor = self.conect_postgres()
        self.migrate_users(cursor)

    def conect_postgres(self):



        # Configuración de conexión
        host = '89.116.73.100'  # Cambia esto por la dirección de tu servidor
        port = 5432  # Puerto
        dbname = 'villasur'  # Nombre de la base de datos
        user = 'odoo'  # Tu usuario
        password = 'RVFERo%gE65ZJcpf4Xz%'  # Tu contraseña

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
    name   = fields.Char(required=True)
    ignore = fields.Boolean(string="Ignorar")
    migrate_model_id = fields.Many2one('migrate.model.jz')


class MigrateModelJz(models.Model):
    _name = 'migrate.model.jz'
    model_id = fields.Many2one('ir.model',string="Modelo")
    table = fields.Char(required=True)
    columns = fields.One2many('migrate.model.columns.jz','migrate_model_id')
    log = fields.Text()
    migrate_id = fields.Many2one('migrate.jz')
    name = fields.Char(related='table')


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

            column_names = [desc[0] for desc in cursor.description]

            self.columns = None
            for cname in column_names:
                self.columns += self.env['migrate.model.columns.jz'].new({
                    'name': cname
                })
        except:
            self.columns = None

    def migrate_table(self):
        cursor = self.migrate_id.conect_postgres()

        select_columnsx = []

        for colx in self.columns:
            #raise ValueError([col,col.ignore])
            if colx.ignore == True:
                continue
                #continue

            select_columnsx.append(colx.name)
            if colx.ignore :
                raise ValueError([colx,colx.ignore,colx.name])


        #raise ValueError(select_columnsx)

        self._migrate_table(cursor, select_columnsx)



    def _migrate_table(self,cursor,select_columns):
        table = self.table
        string_columns = ",".join(select_columns)
        string_sql = f"SELECT {string_columns} FROM {table}"
        if table == 'res_users':
            string_sql += f'  where id != {self.env.user.id} ;'
        cursor.execute(string_sql)
        self.insert_record_migrate(cursor, table,select_columns)



        #resultados = cursor.fetchall()




    def insert_record_migrate(self,cursor,table,column_names):
        resultados = cursor.fetchall()  # Obtener todos los resultados
        #raise ValueError(resultados)

        #raise ValueError(column_names)

        n = len(column_names)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('%s' for _ in range(n))

        # Generar la instrucción INSERT
        for fila in resultados:
            val1 = ','.join(column_names)
            val2 = corchetes_n
            val3 = ','.join(
                "{} = EXCLUDED.{}".format(col, col) for col in column_names
                if col != 'id'
            )

            # raise ValueError(val3)

            SQL_INSERT = f"INSERT INTO {table} ({val1}) VALUES ({val2}) ON CONFLICT (id) DO UPDATE SET {val3}"

            # raise ValueError([len(fila),])
            '''
            self.env.cr.execute(SQL_INSERT, fila)
            '''
            try:
                self.env.cr.execute(SQL_INSERT, fila)
            except:
                raise ValueError([fila,SQL_INSERT])
                sql_strr = "SELECT * FROM product_template  "
                self.env.cr.execute(sql_strr)
                result = self.env.cr.fetchall()
                raise ValueError(result)
                raise ValueError([SQL_INSERT,fila,result])



            # raise ValueError(SQL_INSERT)

            # insert_query = sql.SQL(SQL_INSERT)
            # Ejecutar la instrucción
            # raise ValueError(SQL_INSERT)
            # cursor.execute(SQL_INSERT, fila)



