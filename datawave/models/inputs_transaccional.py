from odoo import models, fields

class StockTienda(models.Model):
    _name = 'datawave.stock.tienda'
    _description = 'StockTienda de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_tienda = fields.Char(string='Tienda_ID')
    stock = fields.Integer(string='Stock')
    date = fields.Date(string='Fecha')


class StockCD(models.Model):
    _name = 'datawave.stock.cd'
    _description = 'StockCD de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    stock = fields.Integer(string='Stock')
    date = fields.Date(string='Fecha')
    code_seller = fields.Char(string='Proveedor ID')

class VentasHistoricas(models.Model):
    _name = 'datawave.sale'
    _description = 'Ventas Historicas de Datawave'
    date = fields.Date(string='Fecha')
    code_tienda = fields.Char(string='Tienda_ID')
    sku = fields.Char(string='Producto_ID')
    quantity = fields.Integer(string="Cantidad")

class OrdenesTransitoCdDetalle(models.Model):
    _name = 'datawave.order.cd'
    _description = 'OrdenesTransitoCdDetalle de Datawave'
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    code_oc = fields.Char(string='OC_ID')
    quantity = fields.Integer(string="Cantidad")
    quantity_waiting = fields.Integer(string="Cantidad Pendiente")
    date = fields.Date(string='Fecha')
    date_arrival = fields.Date(string='Fecha Llegada')
    load_time = fields.Float(string='LeadTime')
    code_seller = fields.Char(string='Proveedor ID')


class TransitoCdResumen(models.Model):
    _name = 'datawave.transit.cd.resume'
    _description = 'TransitoCdResumen de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    stock = fields.Integer(string='Stock')


