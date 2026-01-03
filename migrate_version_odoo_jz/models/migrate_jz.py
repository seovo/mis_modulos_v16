from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql


class MigrateJz(models.Model):
    _name = 'migrate.jz'
    #_rec_name =
    host = fields.Char(string="IP del Servidor Postgres",required=True)
    port = fields.Integer(string="Puerto Postgres",default=5432)
    dbname = fields.Char(string="Base de Datos Postgres",required=True)
    user   = fields.Char(string="Usuario Postgres",required=True)
    password = fields.Char(string="Contraseña Postgres",required=True)
    model_ids = fields.One2many('migrate.model.jz','migrate_id',string="Modelos")
    log = fields.Text()
    from_version = fields.Integer()




    field_ids = fields.One2many('migrate.ir.model.fields','migrate_id',string="Modelos")
    journal_migration_ids = fields.One2many('journal.migration.jz','migrate_id')
    text_journal = fields.Text()
    currency_migration_ids = fields.One2many('currency.migration.jz','migrate_id')
    text_currency = fields.Text()
    account_migration_ids = fields.One2many('account.migration.jz','migrate_id')
    text_account = fields.Text()
    tax_migration_ids = fields.One2many('tax.migration.jz','migrate_id')
    text_tax = fields.Text()
    location_migration_ids = fields.One2many('location.migration.jz','migrate_id')
    text_location = fields.Text()
    country_migration_ids = fields.One2many('country.migration.jz', 'migrate_id')
    text_country = fields.Text()
    state_migration_ids = fields.One2many('state.migration.jz', 'migrate_id')
    text_state = fields.Text()
    city_migration_ids = fields.One2many('city.migration.jz', 'migrate_id')
    text_city = fields.Text()


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

    def generate_text_journal(self):

        if self.currency_migration_ids and not self.text_currency:

            id_journal = ''

            for migrat in self.currency_migration_ids:
                if not migrat.currency_id:
                    continue
                id_journal += f''' WHEN currency_id = {migrat.id_sql} THEN {migrat.currency_id.id } \n'''

            textx = f'''
            CASE
               {id_journal}
            ELSE   currency_id
            END AS currency_id
            '''

            self.text_currency = textx

        if self.journal_migration_ids and not self.text_journal:

            id_journal = ''

            for migrat in self.journal_migration_ids:
                if not migrat.journal_id:
                    continue
                id_journal += f''' WHEN journal_id = {migrat.id_sql} THEN {migrat.journal_id.id } \n'''

            textx = f'''
            CASE
               {id_journal}
            ELSE   journal_id
            END AS journal_id
            '''

            self.text_journal =textx

        if self.account_migration_ids and not self.text_account:

            id_journal = ''

            for migrat in self.account_migration_ids:
                if not migrat.account_id:
                    continue
                id_journal += f''' WHEN account_id = {migrat.id_sql} THEN {migrat.account_id.id } \n'''

            textx = f'''
            CASE
               {id_journal}
            ELSE   account_id
            END AS account_id
            '''

            self.text_account =textx

        if self.tax_migration_ids and not self.text_tax:

            id_journal = ''

            for migrat in self.tax_migration_ids:
                if not migrat.tax_id:
                    continue
                id_journal += f''' WHEN account_tax_id = {migrat.id_sql} THEN {migrat.tax_id.id } \n'''

            textx = f'''
            CASE
               {id_journal}
            ELSE   account_tax_id
            END AS account_tax_id
            '''

            self.text_tax =textx

        if self.location_migration_ids and not self.text_location:

            id_journal = ''

            for migrat in self.location_migration_ids:
                if not migrat.location_id:
                    continue
                id_journal += f''' WHEN location_id = {migrat.id_sql} THEN {migrat.location_id.id } \n'''

            textx = f'''
            CASE
               {id_journal}
            ELSE   location_id
            END AS location_id
            '''

            self.text_location =textx

        if self.country_migration_ids and not self.text_country:

            id_countrys = ''

            for migrat in self.country_migration_ids:
                if not migrat.country_id:
                    continue
                id_countrys  += f''' WHEN country_id = {migrat.id_sql} THEN {migrat.country_id.id } \n'''

            textx = f'''
                CASE
                    {id_countrys}
                ELSE  country_id
                END AS country_id
            '''

            self.text_country = textx


        if self.state_migration_ids and not self.text_state:

            id_countrys = ''

            for migrat in self.state_migration_ids:
                if not migrat.state_id:
                    continue
                id_countrys  += f''' WHEN state_id = {migrat.id_sql} THEN {migrat.state_id.id } \n'''

            textx = f'''
                CASE
                    {id_countrys}
                ELSE  state_id
                END AS state_id
            '''

            self.text_state = textx






    def add_modelos_usuales(self):


        #self.env.cr.execute("TRUNCATE TABLE account_tax_purchase_order_line_rel ;")



        #self.env.cr.execute("TRUNCATE TABLE product_taxes_rel ;")
        #self.env.cr.execute("TRUNCATE TABLE product_supplier_taxes_rel ;")

        self.generate_text_journal()


        tablas = [
            'res_partner','res_users','product_category',

            'product_template','product_product','product_taxes_rel','product_supplier_taxes_rel',
                  
            'account_journal','res_currency','account_account','account_move','account_move_line',
            'account_move_line_account_tax_rel',
            'account_payment','sale_order','sale_order_line',

            'purchase_order','purchase_order_line','purchase_order_stock_picking_rel',

            'account_tax','account_tax_purchase_order_line_rel','stock_location',
            'stock_picking','stock_move','stock_move_line','stock_quant',

            'product_supplierinfo',

            'res_country','res_country_state','res_city' ,

            'account_full_reconcile','account_partial_reconcile',

        ]

        if self.from_version == 11:
            tablas.append("account_invoice")
            tablas.append("account_invoice_line")
            tablas.append("account_invoice_payment_rel")




        for table in tablas:
            table_object = self.env['migrate.model.jz'].search([('migrate_id','=', self.id),('table','=',table)])

            if not table_object:
                table_object = self.env['migrate.model.jz'].create({
                    'migrate_id': self.id ,
                    'table': table
                })

                if table == 'account_invoice_line':
                    table_object.identificador = 'name , invoice_id'
                    table_object.update_if_exist = True
                    table_object.new_table = 'account_invoice_line'

                if table == 'account_account':
                    table_object.where_set = '''
                    
                    id IN (  SELECT DISTINCT aml.account_id  FROM account_move_line aml )
                    
                    '''

                table_object.change_table()


        #para los campos que son journal_id
        jurnal_fields= self.env['migrate.model.columns.jz'].search([('name','=','journal_id')])

        for jfiels in jurnal_fields:
            jfiels.value_set = self.text_journal

        currency_fields= self.env['migrate.model.columns.jz'].search([('name','=','currency_id')])

        for jfiels in currency_fields:
            jfiels.value_set = self.text_currency


        account_fields = self.env['migrate.model.columns.jz'].search([('name','=','account_id')])

        for jfiels in account_fields:
            jfiels.value_set = self.text_account

        tax_fields = self.env['migrate.model.columns.jz'].search([('name','=','account_tax_id')])

        for jfiels in tax_fields:
            jfiels.value_set = self.text_tax

        tax_fields2 = self.env['migrate.model.columns.jz'].search([('name', '=', 'tax_id')])

        for jfiels2 in tax_fields2:

            text_tax = self.text_tax

            text_tax = text_tax.replace('account_tax_id','tax_id')

            jfiels2.value_set = text_tax

        location_fields = self.env['migrate.model.columns.jz'].search([('name','=','location_id')])

        for jfiels in location_fields:
            jfiels.value_set = self.text_location

        country_fields = self.env['migrate.model.columns.jz'].search([('name', '=', 'country_id')])

        for jfiels in country_fields:
            jfiels.value_set = self.text_country

        state_fields = self.env['migrate.model.columns.jz'].search([('name', '=', 'state_id')])

        for jfiels in state_fields:
            jfiels.value_set = self.text_state

        #location_id




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

    def update_computes_funciones_migraciones(self):

        cron_models = self.env['migrate.model.jz'].search([('is_part_cron','=',True)],limit=1)

        if cron_models:
            cron_models.migrate_table()
            return



        moves_without_partner = self.env['account.move'].search([
            ('partner_id','!=',False),

            ('invoice_partner_display_name','=',False)],limit=1000)

        if moves_without_partner:
            moves_without_partner._compute_invoice_partner_display_info()
            return



        moveslines_without_amount = self.env['account.move.line'].search([
           ('amount_currency', '=',0),
            ('move_id.move_type', '!=', 'entry'),
            ('display_type', '=', 'product'),
            ('account_id.account_type', '!=', 'off_balance'),
            ('move_id', '!=', False),
            ('currency_id','=',self.env.ref('base.PEN').id) ,
            #('move_id','=',59)
        ])

        #raise ValidationError(str(moveslines_without_amount))

        if moveslines_without_amount:
            for mvl in moveslines_without_amount:

                line = mvl

                #raise ValidationError(str([line.move_id.is_invoice(True),line.move_id.move_type,line.move_id.get_sale_types(True)]))

                #raise ValidationError(str([line.currency_id,line.company_id.currency_id,line.move_id.is_invoice(True)]))

                if line.amount_currency == 0:

                    tt = line.currency_id.round(line.balance * line.currency_rate)

                    #raise ValidationError(tt)
                    sql = f'''UPDATE account_move_line SET amount_currency = %s  WHERE id = %s'''
                    self.env.cr.execute(sql,[tt,line.id])
                    #line.amount_currency = tt


            return



        moves = self.env['account.move'].search([
            ('amount_total_in_currency_signed', '=', 0),
            ('move_type', '!=', 'entry'),
            ('state','=','posted'),
            ('currency_id','=',self.env.ref('base.PEN').id) ,], limit=200)

        if moves:

            for mv in moves:
                try:
                    mv._compute_amount()
                except:
                    #raise ValidationError(mvl.move_id)
                    continue


            return

        moveslines_without_amount = self.env['account.move.line'].search([
            ('price_subtotal', '=', 0),
            ('move_id.move_type', '!=', 'entry'),
            ('display_type','=','product'),
            ('price_unit','!=',0),
            ('account_id.account_type','!=','off_balance'),
            ('move_id', '!=', False),
        ], limit=50)

        #raise ValidationError(moveslines_without_amount)

        if moveslines_without_amount:
            for mvl in moveslines_without_amount:

                # raise ValidationError(mvl.move_id)

                try:
                    mvl._compute_totals()
                except:
                    #raise ValidationError(mvl.move_id)
                    continue

            return



        raise ValidationError('BBB')

        moves_without_amount = self.env['account.move'].search([
            ('amount_total', '=', 0),
            ('move_type','!=','entry'),

            ('invoice_line_ids', '!=', False)], limit=500)

        #raise ValidationError(moves_without_amount)

        if moves_without_amount :
            for mw in moves_without_amount:

                try:

                    mw._inverse_amount_total()
                    mw._compute_amount()

                except:
                    continue
                    raise ValidationError(mw)



            return

        moves_without_payment = self.env['account.move'].search([
            ('payment_state', '=', 'not_paid'),
            # ('status_in_payment', '!=', 'paid'),
            ('state', '=', 'posted'),
            # ('move_type', 'in', ['out_invoice', 'out_refund']),
            ("matched_payment_ids", "!=", False)], limit=10)

        # raise ValidationError(moves_without_payment)

        if moves_without_payment:
            for paymentm in moves_without_payment:

                try:
                    # paymentm._compute_amount()
                    paymentm._compute_payment_state()
                except:
                    # raise ValidationError(paymentm)
                    continue

            return





