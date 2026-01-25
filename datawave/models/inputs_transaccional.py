from odoo import models, fields

class StockTienda(models.Model):
    _name = 'datawave.stock.tienda'
    _description = 'StockTienda de Datawave'
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    tienda_id = fields.Many2one('datawave.tienda', string='Tienda', required=True)

    stock = fields.Integer(string='Stock')
    date = fields.Date(string='Fecha')

'''

class StockCD(models.Model):
    _name = 'datawave.stock.cd'
    _description = 'StockCD de Datawave'

    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    cd_id = fields.Many2one('datawave.cd', string='CD')
    stock = fields.Integer(string='Stock')
    date = fields.Date(string='Fecha')
    seller_id = fields.Many2one('datawave.seller',string='Proveedor')
    
'''

class VentasHistoricas(models.Model):
    _name = 'datawave.sale'
    _description = 'Ventas Historicas de Datawave'
    date = fields.Date(string='Fecha', required=True)
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    tienda_id = fields.Many2one('datawave.tienda', string='Tienda', required=True)
    quantity = fields.Integer(string="Cantidad")


class VentasHistoricasCD(models.Model):
    _name = 'datawave.sale,cd'
    _description = 'Ventas Historicas de Datawave'
    date = fields.Date(string='Fecha', required=True)
    product_id = fields.Many2one('datawave.producto', string='Producto', required=True)
    cd_id = fields.Many2one('datawave.cd', string='CD')
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


