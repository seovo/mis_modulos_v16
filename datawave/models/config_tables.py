from odoo import models, fields

class ConfigTiendaProducto(models.Model):
    _name = 'datawave.config.tienda.product'
    _description = 'ConfigTiendaProducto de Datawave'

    product_id   =  fields.Many2one('datawave.producto',string='Producto',required=True)
    tienda_id    = fields.Many2one('datawave.tienda',string='Tienda',required=True)
    days_target  = fields.Integer(string='Días objetivo')
    lt_days      = fields.Integer(string='LT')
    z_tienda     = fields.Float(string='Z')
    round_tienda = fields.Float(string='Redondeo min')


class ConfigTienda(models.Model):
    _name = 'datawave.config.tienda'
    _description = 'ConfigTienda de Datawave'

    tienda_id           = fields.Many2one('datawave.tienda',string='Tienda',required=True)
    days_delta          = fields.Integer(string='Delta Dias')
    days_frequency      = fields.Integer(string='Frecuencia fija')
    z_tienda            = fields.Float(string='Z')