from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def show_lot_availables(self):
        self.conect_postgres()

    def conect_postgres(self):
        import psycopg2
        from psycopg2 import sql

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

        # Realizar una consulta (ejemplo)
        cursor.execute("SELECT * FROM res_partner;")
        db_version = cursor.fetchall()

        raise ValueError(db_version)

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

