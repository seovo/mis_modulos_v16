from odoo import api, fields, models

class IntermedioGenerador(models.TransientModel):
    _name = "intermedio.generador"
    _description = "intermedio.generador"
    date      = fields.Date(string='Fecha',required=True)
    date_end  = fields.Date(string='Fecha Fin')
    table      = fields.Selection([
        ('intermedio_cd','Intemredio CD'),
        ('intermedio_tienda','Intermedio Tienda')
    ],string='Tabla',required=True)

    def generate_table(self):
        if self.date_end:
            domain = [('')]
        else:
            pass
