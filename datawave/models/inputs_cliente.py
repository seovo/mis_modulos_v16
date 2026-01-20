from odoo import models, fields

class Producto(models.Model):
    _name = 'datawave.producto'
    _description = 'Productos de Datawave'

    name = fields.Char(string='SKU')
    description = fields.Char(string='Nombre', required=True)
    categ = fields.Char(string='Categoría')
    uom = fields.Char(string='Unidad de Medida')
    state = fields.Char(string='Estado')

class Tienda(models.Model):
    _name = 'datawave.tienda'
    _description = 'Tienda de Datawave'

    name    = fields.Char(string='Tienda Id')
    description    = fields.Char(string='Nombre', required=True)
    region  = fields.Char(string='Region')
    type    = fields.Char(string='Tipo')

class CentroDistribucion(models.Model):
    _name = 'datawave.cd'
    _description = 'CentroDistribucion de Datawave'

    name    = fields.Char(string='CD_ID')
    description   = fields.Char(string='Nombre', required=True)
    region  = fields.Char(string='Region')
    type    = fields.Char(string='Tipo')


class Proveedores(models.Model):
    _name = 'datawave.seller'
    _description = 'Proveedores de Datawave'

    name       = fields.Char(string='Proveedor_ID')
    description       = fields.Char(string='Nombre', required=True)
    load_time  = fields.Float(string='LeadTime (días)')
    frequency  = fields.Float(string='Frecuencia empírica')
    cost_sale  = fields.Float(string='Costo pedido')
    cost_keep  = fields.Float(string='Costo mantener')
    review_cycle = fields.Float(string='Ciclo revisión')
    frequency_fixed = fields.Float(string='Frecuencia Fija')
    moq_default     = fields.Float(string='Moq Default')

class CentroDistribucion(models.Model):
    _name = 'datawave.tienda.cd'
    _description = 'Tienda CentroDistribucion de Datawave'

    code_tienda    = fields.Char(string='Tienda ID', required=True)
    code_cd        = fields.Char(string='CD_ID', required=True)




