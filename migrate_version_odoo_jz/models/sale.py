from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
        from psycopg2 import sql

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def show_lot_availables(self):
        self.conect_postgres()

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

        resultados = cursor.fetchall()  # Obtener todos los resultados
        column_names = [desc[0] for desc in cursor.description]

        # Generar la instrucción INSERT
        for fila in resultados:

            val1 = sql.SQL(', ').join(map(sql.Identifier, column_names))
            val2 = sql.SQL(', ').join(map(sql.Placeholder, column_names))
            val3 = sql.SQL(', ').join(
                    sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col)) for col in column_names
                    if col != 'id'
                )


            SQL_INSERT = f"INSERT INTO res_partner ({val1}) VALUES ({val2}) ON CONFLICT (id) DO UPDATE SET {val3}"

            insert_query = sql.SQL(SQL_INSERT)
            # Ejecutar la instrucción
            raise ValueError(SQL_INSERT)
            cursor.execute(insert_query, fila)


        try:
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

            # Realizar una consulta (ejemplo)
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"Versión de la base de datos: {db_version}")

        except Exception as e:
            print(f"Ocurrió un error: {e}")

        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Conexión cerrada.")

