from odoo import api, fields, models
from odoo.exceptions import UserError

class IntermedioGenerador(models.TransientModel):
    _name = "intermedio.generador"
    _description = "intermedio.generador"
    date      = fields.Date(string='Fecha',required=True)
    date_end  = fields.Date(string='Fecha Fin')
    table      = fields.Selection([
        ('intermedio_cd','Intermedio CD'),
        ('intermedio_tienda','Intermedio Tienda')
    ],string='Tabla',required=True)

    def generate_table(self):


        productos = self.env['datawave.producto'].search([])
        dates = [self.date]

        if self.date_end :
            if self.date_end <= self.date :
                raise UserError('LA FECHA FIN DEBE SER MAYOR A LA FECHA')

            DIFF = self.date_end - self.date
            raise UserError(DIFF.days)

        if self.table == 'intermedio_cd':
            cdis = self.env['datawave.cd'].search([])
            proveedores = self.env['datawave.seller'].search([])

            for product in productos:
                for cdi in cdis:
                    for datee in dates:

                        for seller in proveedores:
                            exist = self.env['datawave.intermedio.cd'].search(
                                [
                                    ('product_id', '=', product.id),
                                    ('cd_id', '=', cdi.id),
                                    ('date', '=', datee),
                                    ('seller_id','=',seller.id)
                                ]
                            )

                            if not exist:
                                exist = self.env['datawave.intermedio.cd'].create({
                                    'product_id': product.id,
                                    'cd_id': cdi.id,
                                    'date': datee ,
                                    'seller_id': seller.id
                                })



                        exist.change_product_tienda()

            #raise ValueError('HOLA')
            return {
                "name": ("DATA ACTULIZADA"),
                "type": "ir.actions.act_window",
                "view_mode": "list,form",
                "res_model": "datawave.intermedio.cd",
                "domain": [("date", "in", dates)],
                "target": "current"
            }


        if self.table == 'intermedio_tienda':
            tiendas = self.env['datawave.tienda'].search([])

            #raise ValueError([tiendas,productos])

            for product in productos:
                for tienda in tiendas:
                    for datee in dates:
                        exist = self.env['datawave.intermedio.tienda'].search(
                            [
                                ('product_id','=',product.id),
                                ('tienda_id','=',tienda.id),
                                ('date','=',datee)
                            ]
                        )

                        if not exist:

                            exist = self.env['datawave.intermedio.tienda'].create({
                                'product_id': product.id ,
                                'tienda_id': tienda.id ,
                                'date': datee
                            })

                        exist.change_product_tienda()

            #raise ValueError('HOLA')
            return {
                "name": ("DATA ACTULIZADA"),
                "type": "ir.actions.act_window",
                "view_mode": "list,form",
                "res_model": "datawave.intermedio.tienda",
                "domain": [("date", "in", dates)],
                "target": "current"
            }


