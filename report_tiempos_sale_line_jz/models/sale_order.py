from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    client_order_ref = fields.Char(related='order_id.client_order_ref', string="Referencia cliente")
    default_code = fields.Char(related='product_id.default_code',string="Referencia Interna")

    move_reference = fields.Char(compute='get_data_report_time',string='Stock Referencia')
    purchase_id = fields.Many2one('purchase.order',compute='get_data_report_time',string="Compra")
    purchase_create_date = fields.Datetime(compute='get_data_report_time',string="Fecha Creada Compra")
    purchase_date_order = fields.Datetime(compute='get_data_report_time', string="Fecha Compra")
    purchase_create_uid = fields.Many2one('res.users',compute='get_data_report_time', string="Compra creado por")
    purchase_product_qty = fields.Float( compute='get_data_report_time', string="Compra Cantidad")
    purchase_price_unit = fields.Float(compute='get_data_report_time', string="Compra P. Unit")
    purchase_qty_received = fields.Float(compute='get_data_report_time', string="Compra Cant Recibida")
    purchase_product_uom_qty = fields.Float(compute='get_data_report_time', string="Compra Cant Total")
    purchase_date_planned = fields.Datetime(compute='get_data_report_time', string="Fecha Prevista")
    purchase_partner_id    = fields.Many2one('res.partner', compute='get_data_report_time', string="Proveedor")
    purchase_currency_id   = fields.Many2one('res.currency', compute='get_data_report_time', string="Compra Moneda")
    purchase_paqueteria    = fields.Char(string="Paqueteria", compute='get_data_report_time')
    purchase_guia_envio    = fields.Char(string="Guia de Envio", compute='get_data_report_time')

    qty_to_deliver_store   = fields.Float(related='qty_to_deliver',store=True)

    def get_data_report_time(self):
        for record in self:

            record.move_reference = record.move_ids[0].reference if record.move_ids else None

            purchase_line = record.move_ids[0].created_purchase_line_id if record.move_ids else None

            record.purchase_id = purchase_line.order_id.id if purchase_line else None
            record.purchase_create_date = purchase_line.order_id.create_date if purchase_line else None
            record.purchase_date_order = purchase_line.order_id.date_order if purchase_line else None
            record.purchase_create_uid = purchase_line.order_id.create_uid.id if purchase_line else None
            record.purchase_partner_id = purchase_line.order_id.partner_id.id if purchase_line else None
            record.purchase_product_qty = purchase_line.product_qty if purchase_line else None
            record.purchase_qty_received = purchase_line.qty_received if purchase_line else None
            record.purchase_product_uom_qty = purchase_line.product_uom_qty if purchase_line else None
            record.purchase_date_planned = purchase_line.date_planned if purchase_line else None
            record.purchase_price_unit = purchase_line.price_unit if purchase_line else None
            record.purchase_currency_id = purchase_line.currency_id.id if purchase_line else None
            record.purchase_paqueteria = purchase_line.x_studio_x_paqueteria  if purchase_line else None
            record.purchase_guia_envio = purchase_line.x_studio_x_guia_envio  if purchase_line else None
