from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql


class MigrateJz(models.Model):
    _name = 'migrate.jz'
    _rec_name =  'host'
    host = fields.Char(string="IP del Servidor Postgres",required=True)
    port = fields.Integer(string="Puerto Postgres",default=5432)
    dbname = fields.Char(string="Base de Datos Postgres",required=True)
    user   = fields.Char(string="Usuario Postgres",required=True)
    password = fields.Char(string="Contraseña Postgres",required=True)
    model_ids = fields.One2many('migrate.model.jz','migrate_id',string="Modelos")
    log = fields.Text()
    from_version = fields.Integer()
    current_version = fields.Integer()

    field_ids = fields.One2many('migrate.ir.model.fields','migrate_id',string="Modelos")
    journal_migration_ids = fields.One2many('journal.migration.jz','migrate_id')
    text_journal = fields.Text()
    currency_migration_ids = fields.One2many('currency.migration.jz','migrate_id')
    text_currency = fields.Text()
    account_migration_ids = fields.One2many('account.migration.jz','migrate_id')
    text_account = fields.Text()

    tax_migration_ids = fields.One2many('tax.migration.jz','migrate_id')
    text_tax = fields.Text()

    tax_group_migration_ids = fields.One2many('tax.group.migration.jz', 'migrate_id')
    text_tax_group = fields.Text()

    account_type_migration_ids = fields.One2many('account.type.migration.jz', 'migrate_id')
    text_account_type = fields.Text()

    account_group_migration_ids = fields.One2many('account.group.migration.jz', 'migrate_id')
    text_account_group = fields.Text()

    location_migration_ids = fields.One2many('location.migration.jz','migrate_id')
    text_location = fields.Text()
    country_migration_ids = fields.One2many('country.migration.jz', 'migrate_id')
    text_country = fields.Text()
    state_migration_ids = fields.One2many('state.migration.jz', 'migrate_id')
    text_state = fields.Text()
    city_migration_ids = fields.One2many('city.migration.jz', 'migrate_id')
    text_city = fields.Text()
    pricelist_migration_ids = fields.One2many('pricelist.migration.jz', 'migrate_id')
    text_pricelist = fields.Text()




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

                self.field_ids.unlink()

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

    def generate_text_set_clave(self):

        if self.account_group_migration_ids:
            id_account_group = ''

            for migrat in self.account_group_migration_ids:
                if not migrat.account_group_id:
                    continue
                id_account_group += f''' WHEN group_id = {migrat.id_sql} THEN '{migrat.account_group_id.id}' \n'''

            textx = f'''
                        CASE
                            {id_account_group}
                        ELSE  group_id
                        END AS group_id
            '''
            self.text_account_group = textx

        if self.account_type_migration_ids:
            id_tax_group = ''

            for migrat in self.account_type_migration_ids:
                if not migrat.account_type:
                    continue
                id_tax_group += f''' WHEN user_type_id = {migrat.id_sql} THEN '{migrat.account_type}' \n'''

            textx = f'''
                        CASE
                           {id_tax_group}
                        ELSE  'off_balance'
                        END AS account_type
                        '''

            self.text_account_type = textx

        if self.tax_group_migration_ids:
            id_tax_group = ''

            for migrat in self.tax_group_migration_ids:
                if not migrat.tax_group_id:
                    continue
                id_tax_group += f''' WHEN tax_group_id = {migrat.id_sql} THEN {migrat.tax_group_id.id } \n'''

            textx = f'''
                        CASE
                           {id_tax_group}
                        ELSE  tax_group_id
                        END AS tax_group_id
                        '''

            self.text_tax_group = textx

        if self.currency_migration_ids :

            id_journal = ''

            for migrat in self.currency_migration_ids:
                if not migrat.currency_id:
                    continue
                id_journal += f''' WHEN currency_id = {migrat.id_sql} THEN {migrat.currency_id.id } \n'''

            #MONEDA
            #self.env.ref('base.USD').id

            textx = f'''
            CASE
               {id_journal}
            ELSE   { self.env.company.currency_id.id }
            END AS currency_id
            '''

            self.text_currency = textx

        if self.journal_migration_ids :

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

        if self.account_migration_ids :

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

        if self.tax_migration_ids :

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

        if self.location_migration_ids :

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

        if self.country_migration_ids :

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


        if self.state_migration_ids :

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

        if self.pricelist_migration_ids :

            id_pricelist = ''

            for migrat in self.pricelist_migration_ids:
                if not migrat.pricelist_id:
                    continue
                id_pricelist  += f''' WHEN pricelist_id = {migrat.id_sql} THEN {migrat.pricelist_id.id } \n'''

            textx = f'''
                CASE
                    {id_pricelist}
                ELSE  pricelist_id
                END AS pricelist_id
            '''

            self.text_pricelist = textx


    def get_tables_maestros(self):
        tables_maestros = [
            'account_group','account_account','account_tax_group','product_pricelist','account_journal','res_currency',
            'account_tax','stock_location'
        ]

        if self.from_version in [11,12]:
            tables_maestros.append("account_account_type")
        return tables_maestros

    def add_modelos_usuales(self):
        #self.env.cr.execute("TRUNCATE TABLE account_tax_purchase_order_line_rel ;")
        #self.env.cr.execute("TRUNCATE TABLE product_taxes_rel ;")
        #self.env.cr.execute("TRUNCATE TABLE product_supplier_taxes_rel ;")

        self.generate_text_set_clave()


        tablas = self.get_tables_maestros()  + [
            'res_partner','res_users','product_category',
            'product_template','product_product',
            'product_taxes_rel','product_supplier_taxes_rel',
            'sale_order', 'sale_order_line', 'account_tax_sale_order_line_rel',
            'account_move', 'account_move_line', 'account_move_line_account_tax_rel',
            'account_payment',
            'purchase_order','purchase_order_line','purchase_order_stock_picking_rel',
            'account_tax_purchase_order_line_rel',
            'stock_picking','stock_move','stock_move_line','stock_quant',
            'product_supplierinfo',
            'res_country','res_country_state','res_city' ,
            'account_full_reconcile','account_partial_reconcile',
        ]

        if self.from_version in [11,12]:
            tablas.append("account_invoice")
            tablas.append("account_invoice_line")
            tablas.append("account_invoice_payment_rel")

        #if self.from_version == 11:



        for table in tablas:
            table_object = self.env['migrate.model.jz'].search([('migrate_id','=', self.id),('table','=',table)])

            table_model = table.replace('_', '.')

            model_object = self.env['ir.model'].search([('model', '=', table_model)])

            dict_table_object = {
                'migrate_id': self.id,
                'table': table,
            }

            if model_object:
                dict_table_object.update({
                    'model_id': model_object.id
                })

            if not table_object:


                table_object = self.env['migrate.model.jz'].create(dict_table_object)

                if table == 'account_invoice_line':
                    table_object.identificador = 'name , invoice_id'
                    table_object.update_if_exist = True
                    table_object.new_table = 'account_invoice_line'

                if table in ['account_tax','res_currency']:
                    table_object.where_set = "active = 't' ; "

                if table == 'account_account':
                    table_object.where_set = '''
                    
                    id IN (  SELECT DISTINCT aml.account_id  FROM account_move_line aml )
                    
                    '''

            else:
                table_object.write(dict_table_object)

            table_object.change_table()






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

    def update_currency_migrate_jz(self,moveslines_without_amount):
        for mvl in moveslines_without_amount:

            line = mvl

            # raise ValidationError(str([line.move_id.is_invoice(True),line.move_id.move_type,line.move_id.get_sale_types(True)]))

            # raise ValidationError(str([line.currency_id,line.company_id.currency_id,line.move_id.is_invoice(True)]))

            if line.amount_currency == 0:
                tt = line.currency_id.round(line.balance * line.currency_rate)

                # raise ValidationError(tt)
                sql = f'''UPDATE account_move_line SET amount_currency = %s  WHERE id = %s'''
                # raise  ValidationError([line.balance,line.currency_rate,tt,'-----',line.id])
                self.env.cr.execute(sql, [tt, line.id])
                # line.amount_currency = tt


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
            ('move_id.state', '!=', 'draft'),
            ('display_type', '=', 'product'),
            ('account_id.account_type', '!=', 'off_balance'),
            ('move_id', '!=', False),
            ('currency_id','=',self.env.ref('base.PEN').id) ,
            ('balance','!=',0)
            #('move_id','=',59)
        ])

        #raise ValidationError(str(moveslines_without_amount))

        if moveslines_without_amount:
            self.update_currency_migrate_jz(moveslines_without_amount)


                #raise ValidationError([mvl.move_id,line.amount_currency])


            return



        partials = self.env['account.partial.reconcile'].search([
            '|',('debit_currency_id', '=', False),('credit_currency_id', '=', False)
            ], limit=1000)

        #raise ValidationError(partials)

        if partials:
            for partial in partials:
                #partial._check_required_computed_currencies(no_valid=True)
                #continue
                partial.debit_currency_id = partial.debit_move_id.currency_id
                partial.credit_currency_id = partial.credit_move_id.currency_id


                partial.debit_amount_currency = partial.debit_move_id.amount_currency
                partial.credit_amount_currency = partial.credit_move_id.amount_currency

            return

        moveslines_without_amount = self.env['account.move.line'].search([
            ('price_subtotal', '=', 0),
            ('move_id.move_type', '!=', 'entry'),
            ('display_type', '=', 'product'),
            ('price_unit', '!=', 0),
            ('account_id.account_type', '!=', 'off_balance'),
            ('move_id', '!=', False),
            ('price_unit','>',0.0020)
        ], limit=1000)

        #, limit = 500

        #raise ValidationError(moveslines_without_amount)

        # raise ValidationError(moveslines_without_amount.move_id)

        if moveslines_without_amount:
            for mvl in moveslines_without_amount:
                #mvl._compute_totals()
                #continue

                # raise ValidationError(mvl.move_id)



                #raise ValueError(base_line)

                try:
                    mvl._compute_totals()
                except:

                    #version 18

                    line = mvl

                    base_line = line.move_id._prepare_product_base_line_for_taxes_computation(line)

                    AccountTax = self.env['account.tax']

                    AccountTax._add_tax_details_in_base_line(base_line, line.company_id)

                    price_subtotal = base_line['tax_details']['raw_total_excluded_currency']
                    price_total = base_line['tax_details']['raw_total_included_currency']

                    sql = f''' UPDATE account_move_line SET price_subtotal = %s ,  price_total = %s  WHERE id = {line.id} '''

                    self.env.cr.execute(sql, [price_subtotal,price_total])

                    #raise ValidationError(price_subtotal)

                    #line.price_subtotal = price_subtotal
                    #line.price_total = base_line['tax_details']['raw_total_included_currency']

                    if price_subtotal  == 0:
                        raise ValidationError([mvl.move_id, mvl.id])


                    #raise ValidationError([mvl.move_id,mvl.id])
                    #continue

            return




        #cantidades de inventario

        moves_stock = self.env['stock.move'].search([('quantity','=',False),('move_line_ids','!=',False)],limit=5000)

        if moves_stock:
            for move in moves_stock:
                move._compute_quantity()

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


        moves = self.env['account.move'].search([
            ('amount_total_in_currency_signed', '=', 0),
            ('move_type', '!=', 'entry'),
            ('state','=','posted'),
            #('payment_state','!=','reversed'),
            ('currency_id','=',self.env.ref('base.PEN').id) ,], limit=500)

        if moves:

            #raise ValidationError(moves)

            for mv in moves:
                #mv._compute_amount()
                #continue
                try:
                    mv._compute_amount()
                except:

                    self.update_currency_migrate_jz(mv.invoice_line_ids)

                    #raise ValidationError(mv)
                    #continue


            return





        #raise ValidationError('BBB')

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







