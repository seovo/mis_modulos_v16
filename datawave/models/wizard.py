from odoo import api, fields, models

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

        if self.table == 'intermedio_cd':

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

            raise ValueError('HOLA')
            return {
                "name": ("DATA ACTULIZADA"),
                "type": "ir.actions.act_window",
                "view_mode": "tree,form",
                "res_model": "datawave.intermedio.tienda",
                "domain": [("date", "in", dates)],
                "target": "current"
            }


