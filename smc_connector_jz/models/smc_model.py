from odoo import api, fields, models

class SmcModel(models.Model):
    _name = "smc.model"
    _description = "smc.model"
    move_id = fields.Many2one('account.move')

    cliente = fields.Char()
    rfc  = fields.Char()
    razon_social = fields.Char()
    codigo_postal = fields.Char()
    colonia = fields.Char()
    calle = fields.Char()
    numero_exterior = fields.Char()
    tipo_negocio_area = fields.Char()
    area_empresarial = fields.Char()
    state = fields.Selection([('draft','Pendiente'),('error','Error'),('sent','Enviado')])
    msg = fields.Text()
    xml_sent = fields.Text()

    uuid = fields.Char()
    folio_factura = fields.Char()
    serie = fields.Char()
    fecha_factura = fields.Char()
    tipo_comprobante = fields.Char()
    moneda = fields.Char()
    tipoCambio = fields.Float()
    subtotal = fields.Float()
    descuento = fields.Float()
    iva = fields.Float()
    total = fields.Float()
    line_ids = fields.One2many('smc.model.item','model_id')

class SmcModelItem(models.Model):
    _name = "smc.model.item"
    _description = "smc.model.item"
    model_id = fields.Many2one('smc.model')

    bandera_flete_incluido_en_precio = fields.Char()
    codigo_interno = fields.Char()
    codigo_japon = fields.Char()
    cantidad = fields.Integer()
    precio_lista = fields.Float()
    precio_venta = fields.Float()
    monto_unitario_flete = fields.Float()
    descuento_por_partida = fields.Float()
    lineaFactura = fields.Integer()