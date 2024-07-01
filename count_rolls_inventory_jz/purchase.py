from odoo import api, fields, models
from odoo.exceptions import UserError

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'



class StockPicking(models.Model):
    _inherit       = 'stock.picking'

    def button_validate(self):
        for record in self:
            for line in record.move_line_ids:
                if not line.weight_roll:
                    raise UserError('NO INDICARON PESO DEL ROLLO')



        res = super().button_validate()
        for record in self:
            if record.state == 'done':
                for line in record.move_ids_without_package:
                    if line.state == 'done' and line.product_id:



                        if self.location_id.usage in ['supplier']:
                            quant = self.env['stock.quant'].search([
                                ('location_id', '=', line.location_dest_id.id),
                                ('product_id', '=', line.product_id.id),
                            ])
                            qty_rolls = quant.qty_rolls or 0
                            quant.qty_rolls = qty_rolls + line.qty_rolls

                        if self.location_id.usage == 'internal':
                            quant = self.env['stock.quant'].search([
                                ('location_id', '=', line.location_id.id),
                                ('product_id', '=', line.product_id.id),
                            ])
                            qty_rolls = quant.qty_rolls or 0
                            quant.qty_rolls = qty_rolls - line.qty_rolls







        return res

class PurchaseOrderLine(models.Model):
    _inherit       = 'purchase.order.line'
    qty_rolls = fields.Float(string="Rollos")

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res.update({
            'qty_rolls': self.qty_rolls
        })
        return res