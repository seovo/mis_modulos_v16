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






        select_columns = [
            'id',
            'company_id',
            'create_date',
            'name',
            'title',
            'parent_id',
            'user_id',
            'state_id',
            'country_id',
            'industry_id',
            'color',
            'commercial_partner_id',
            'create_uid',
            'write_uid',
            #'display_name',
            'ref',
            'lang',
            'tz',
            'vat',
            'company_registry',
            'website',
            'function',
            'type',
            'street',
            'street2',
            'zip',
            'city',
            'email',
            'phone',
            'mobile',
            'commercial_company_name',
            'company_name',
            'date',
            'comment',
            'partner_latitude',
            'partner_longitude',
            'active',
            'employee',
            'is_company',
            'partner_share',
            'write_date',
            #'message_main_attachment_id',
            'message_bounce', 'email_normalized', 'contact_address_complete', 'signup_type', 'signup_expiration', 'signup_token', 'team_id', 'ocn_token', 'partner_gid', 'additional_info', 'phone_sanitized', 'supplier_rank', 'customer_rank', 'invoice_warn', 'invoice_warn_msg', 'debit_limit', 'last_time_entries_checked', 'sale_warn', 'sale_warn_msg', 'city_id', 'street_name', 'street_number', 'street_number2', 'l10n_latam_identification_type_id', 'l10n_pe_district', 'online_partner_information', 'followup_reminder_type', 'purchase_warn', 'purchase_warn_msg', 'picking_warn', 'picking_warn_msg']

        string_columns = ",".join(select_columns)
        cursor.execute(f"SELECT {string_columns} FROM res_partner;")
        resultados = cursor.fetchall()  # Obtener todos los resultados
        column_names = [desc[0] for desc in cursor.description]

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

            #raise ValueError(val3)


            SQL_INSERT = f"INSERT INTO res_partner ({val1}) VALUES ({val2}) ON CONFLICT (id) DO UPDATE SET {val3}"

            #raise ValueError([len(fila),])

            self.env.cr.execute(SQL_INSERT,fila)

            #raise ValueError(SQL_INSERT)

            #insert_query = sql.SQL(SQL_INSERT)
            # Ejecutar la instrucción
            #raise ValueError(SQL_INSERT)
            #cursor.execute(SQL_INSERT, fila)


