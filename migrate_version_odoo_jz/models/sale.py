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
        cursor.execute("SELECT * FROM res_partner;")

        resultados = cursor.fetchall()  # Obtener todos los resultados
        column_names = [desc[0] for desc in cursor.description]

        n = len(resultados)  # Cambia este valor a la cantidad de {} que deseas
        corchetes_n = ','.join('{}' for _ in range(n))


        # Generar la instrucción INSERT
        for fila in resultados:

            val1 = ','.join(column_names)
            val2 = corchetes_n
            val3 = ','.join(
                    "{} = EXCLUDED.{}".format(col, col) for col in column_names
                    if col != 'id'
                )

            raise ValueError(val3)


            SQL_INSERT = f"INSERT INTO res_partner ({val1}) VALUES ({val2}) ON CONFLICT (id) DO UPDATE SET {val3}"

            raise ValueError(SQL_INSERT)

            insert_query = sql.SQL(SQL_INSERT)
            # Ejecutar la instrucción
            #raise ValueError(SQL_INSERT)
            cursor.execute(insert_query, fila)


