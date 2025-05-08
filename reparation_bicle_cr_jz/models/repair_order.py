from odoo import api, Command, fields, models, _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError

class RepairOrder(models.Model):
    _inherit = 'repair.order'
    order_line = fields.One2many('line.repair.order','repair_id')

    def action_create_sale_order(self):
        if any(repair.sale_order_id for repair in self):
            concerned_ro = self.filtered('sale_order_id')
            ref_str = "\n".join(ro.name for ro in concerned_ro)
            raise UserError(_("You cannot create a quotation for a repair order that is already linked to an existing sale order.\nConcerned repair order(s) :\n") + ref_str)
        if any(not repair.partner_id for repair in self):
            concerned_ro = self.filtered(lambda ro: not ro.partner_id)
            ref_str = "\n".join(ro.name for ro in concerned_ro)
            raise UserError(_("You need to define a customer for a repair order in order to create an associated quotation.\nConcerned repair order(s) :\n") + ref_str)
        sale_order_values_list = []
        for repair in self:
            sale_order_values_list.append({
                "company_id": self.company_id.id,
                "partner_id": self.partner_id.id,
                "warehouse_id": self.picking_type_id.warehouse_id.id,
                "repair_order_ids": [Command.link(repair.id)],
            })
        self.env['sale.order'].create(sale_order_values_list)
        # Add Sale Order Lines for 'add' move_ids
        self.move_ids._create_repair_sale_order_line()
        self.order_line._create_repair_sale_order_line()
        return self.action_view_sale_order()



class LineRepairOrder(models.Model):
    _name = 'line.repair.order'
    _description = 'line.repair.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product',required=True)
    name = fields.Text(string='Descriptión',required=True)
    code = fields.Char(string='Codigo')
    price = fields.Float(string='Precio')
    user_id = fields.Many2one('res.users',string='Tecnico Asignado')
    product_ids = fields.Many2many('product.product',string="Piezas Utilizadas")
    repair_id = fields.Many2one('repair.order')
    sale_line_id = fields.Many2one('sale.order.line')

    @api.onchange('product_id')
    def change_product(self):
        for record in self:
            record.name = record.product_id.name or ''
            record.code = record.product_id.default_code or ''

    def _create_repair_sale_order_line(self):
        if not self:
            return
        so_line_vals = []
        for move in self:
            if move.sale_line_id :
                continue
            #product_qty = move.product_uom_qty if move.repair_id.state != 'done' else move.quantity
            product_qty = 1
            so_line_vals.append({
                'order_id': move.repair_id.sale_order_id.id,
                'product_id': move.product_id.id,
                'product_uom_qty': product_qty, # When relying only on so_line compute method, the sol quantity is only updated on next sol creation
                'price_unit': move.price ,
                'name': move.name
                #'move_ids': [Command.link(move.id)],
            })
            #if move.repair_id.under_warranty:
            #    so_line_vals[-1]['price_unit'] = 0.0
            #elif move.price_unit:
            #    so_line_vals[-1]['price_unit'] = move.price_unit

        self.env['sale.order.line'].create(so_line_vals)