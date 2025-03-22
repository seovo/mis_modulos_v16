from odoo import api, fields, models

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    warehouse_jz_id = fields.Many2one('stock.warehouse',compute='get_warehouse_jz_id')

    def get_warehouse_jz_id(self):
        for record in self:

            ware = None

            wares = self.env['stock.warehouse'].search([])
            for war in wares:
                location = war.lot_stock_id
                #quants = self.env['stock.quant'].search([('location_id', 'child_of', [location.id])])

                if record.location_id == location:
                    ware = war.id
                    break


                if record.location_id.location_id == location:
                    ware = war.id
                    break


                #if war.id in quants.ids:
                #    ware = war.id
                #    break

            record.warehouse_jz_id = ware