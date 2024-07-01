from odoo import api, fields, models
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit       = 'stock.quant'
    qty_rolls  = fields.Float(string="Rollos")


class StockMOVE(models.Model):
    _inherit       = 'stock.move'
    qty_rolls  = fields.Float(string="Rollos")

    def write(self,vals):
        res = super().write(vals)

        return res

    @api.onchange('move_line_ids','move_line_ids.qty_rolls')
    def update_qty_rolls(self):
        for record in self:
            qty_rolls = 0
            for line in record.move_line_ids:
                qty_rolls += line.qty_rolls
            record.qty_rolls = qty_rolls



class StockMoveLine(models.Model):
    _inherit       = 'stock.move.line'
    qty_rolls  = fields.Float(string="Rollos")
    weight_roll  = fields.Float(string="Peso Rollo")
    @api.onchange('quantity')
    def change_qty_rolls_quantity(self):
        for record in self:
            weight_rolls = record.quantity
            if record.quantity < 20 or record.quantity > 25 :
                weight_rolls = record.move_id.product_id.weight
            record.weight_roll = weight_rolls
            record.qty_rolls = record.quantity/record.weight_roll if record.weight_roll != 0 else 0

    @api.onchange('weight_roll')
    def change_qty_rolls(self):
        for record in self:
            record.qty_rolls = record.quantity/record.weight_roll if record.weight_roll != 0 else 0


