from odoo import models, fields

class ConfigTiendaProducto(models.Model):
    _name = 'datawave.config.tienda.product'
    _description = 'ConfigTiendaProducto de Datawave'
    product_id =  fields.Many2one('datawave.producto')