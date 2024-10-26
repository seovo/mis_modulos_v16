from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    default_code = fields.Char(related='product_id.default_code',string="Referencia Interna")
    move_reference = fields.Char(compute='get_data_report_time',string='Stock Referencia')
    purchase_id = fields.Many2one('purchase.order',compute='get_data_report_time',string="Compra")
    purchase_create_date = fields.Datetime(compute='get_data_report_time',string="Fecha Creada Compra")
    purchase_date_order = fields.Datetime(compute='get_data_report_time', string="Fecha Compra")
    purchase_create_uid = fields.Many2one('res.users',compute='get_data_report_time', string="Compra creado por")
    purchase_product_qty = fields.Float( compute='get_data_report_time', string="Compra Cantidad")
    purchase_qty_received = fields.Float(compute='get_data_report_time', string="Compra Cant Recibida")
    purchase_product_uom_qty = fields.Float(compute='get_data_report_time', string="Compra Cant Total")


    def get_data_report_time(self):
        for record in self:

            record.move_reference = record.move_ids>[0].reference if record.move_ids else None
            record.purchase_id = record.purchase_line_ids[0].order_id.id if record.purchase_line_ids else None
            record.purchase_create_date = record.purchase_line_ids[0].order_id.create_date if record.purchase_line_ids else None
            record.purchase_date_order = record.purchase_line_ids[
                0].order_id.date_order if record.purchase_line_ids else None
            record.purchase_create_uid = record.purchase_line_ids[
                0].order_id.create_uid.id if record.purchase_line_ids else None
            record.purchase_product_qty = record.purchase_line_ids[
                0].product_qty if record.purchase_line_ids else None
            record.purchase_qty_received = record.purchase_line_ids[
                0].qty_received if record.purchase_line_ids else None
            record.purchase_product_uom_qty = record.purchase_line_ids[
                0].product_uom_qty if record.purchase_line_ids else None
