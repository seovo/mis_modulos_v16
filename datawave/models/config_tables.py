from odoo import models, fields

class ConfigCD(models.Model):
    _name = 'datawave.config.cd'
    _description = 'ConfigCD de Datawave'

    cd_id = fields.Many2one('datawave.cd', string='CD')
    days_delta          = fields.Integer(string='Delta Dias')
    fixed_frequency     = fields.Integer(string='Frecuencia fija')
    z_cd                = fields.Float(string='Z')
    days_target         = fields.Integer(string='Días objetivo')
    cicle_review_day    = fields.Integer(string='Ciclo revisión')

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


class ConfigProveedorProductoCD(models.Model):
    _name = 'datawave.config.proveedor.cd'
    _description = 'ConfigProveedorProductoCD de Datawave'

    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    seller_id = fields.Many2one('datawave.seller', string='Proveedor')
    cd_id = fields.Many2one('datawave.cd', string='CD')
    moq = fields.Float(string='Sigma',default='0')
    lt_days = fields.Integer(string='LT')
    z_tienda = fields.Float(string='Z')
    cost_sale = fields.Float(string='Costo pedido')
    cost_keep = fields.Float(string='Costo mantener')
    frequency_empirical = fields.Float(string='Frecuencia Empirico')
    days_objetive = fields.Integer(string='Dias Objetivos')
    days_delta = fields.Integer(string='Dias Delta')
    round_cd = fields.Float(string='Redondeo Min')
