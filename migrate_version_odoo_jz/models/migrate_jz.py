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


        partner_object = self.env['migrate.model.jz'].search([
            ('migrate_id','=', self.id),('table','=','res_partner')
        ])

        if not partner_object:
            partner_object = self.env['migrate.model.jz'].create({
                'migrate_id': self.id ,
                'table': 'res_partner'
            })


            partner_object.change_table()

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





