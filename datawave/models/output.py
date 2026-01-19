from odoo import models, fields

class ReplanishTienda(models.Model):
    _name = 'datawave.replanish.tienda'
    _description = 'SigmaTienda de Datawave'
    name = fields.Char(string='Clave')
    sku = fields.Char(string='Producto_ID')
    code_tienda = fields.Char(string='Tienda_ID')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')
    note = fields.Text(string='Comentario')

class ReplanishCD(models.Model):
    _name = 'datawave.replanish.cd'
    _description = 'ReplanishCD de Datawave'
    name = fields.Char(string='Clave')
    code = fields.Char(string='Clave2')
    sku = fields.Char(string='Producto_ID')
    code_cd = fields.Char(string='CD_ID')
    code_seller = fields.Char(string='Proveedor ID')
    quantity_round = fields.Integer(string='Cantidad Sugerida Redondeada')
    note = fields.Text(string='Comentario')

class AlertInventario(models.Model):
    _name = 'datawave.alert.stock'
    _description = 'ReplanishCD de Datawave'
    name = fields.Char(string='Clave')
    code = fields.Char(string='Clave2')
    sku            = fields.Char(string='Producto_ID')
    ubicacion      = fields.Char(string='Tienda o CD')
    type_ubicacion = fields.Char(string='Tienda/CD')
    code_seller    = fields.Char(string='Proveedor ID')
    stock = fields.Integer(string='Stock')
    ss = fields.Float(string='SS', help='Z*Sigma*SQRT(LT)')
    rop = fields.Float(string='ROP', help='Forecast*LT+SS')
    max = fields.Float(string='MAX', help='(LT+FREQ)*Forecast+SS')
    risk = fields.Char(string='Riesgo')
    risk_severity =  fields.Char(string='Severidad Riesgo')
    over_stock = fields.Float(string='Sobrestock')
    over_stock_severity = fields.Float(string='Severidad Sobrestock')
