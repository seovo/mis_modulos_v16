from odoo import api, fields, models
from odoo.exceptions import UserError

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'


class StockPicking(models.Model):
    _inherit       = 'stock.picking'

    def button_validate(self):

        for record in self:
            #raise ValueError(record.picking_type_id.code)
            for line in record.move_line_ids:
                if not line.weight_roll:
                    raise UserError('NO INDICARON PESO DEL ROLLO')

        res = super().button_validate()


        for record in self:

            if record.picking_type_id.code == 'internal':
                for linex in record.move_ids_without_package:
                    #raise ValueError(linex.move_line_ids)
                    if len(linex.move_line_ids) == 1:
                        linex.move_line_ids.qty_rolls = linex.qty_rolls




            for line in record.move_line_ids:
                if not line.qty_rolls:
                    raise UserError('NO INDICARON EL NUMERO DE ROLLOS')


        for record in self:
            if record.state == 'done':
                for line in record.move_ids_without_package:
                    if line.state == 'done' and line.product_id:

                        quant_dest = self.env['stock.quant'].search([
                            ('location_id', '=', line.location_dest_id.id),
                            ('product_id', '=', line.product_id.id),
                        ])

                        quant_origin = self.env['stock.quant'].search([
                            ('location_id', '=', line.location_id.id),
                            ('product_id', '=', line.product_id.id),
                        ])



                        if  record.picking_type_id.code in ['internal','incoming']:

                            qty_rolls = quant_dest.qty_rolls or 0
                            quant_dest.qty_rolls = qty_rolls + line.qty_rolls

                            #raise ValueError([record.picking_type_id.code,quant_dest.qty_rolls,line.qty_rolls,qty_rolls])

                        #raise ValueError('ok')

                        if  record.picking_type_id.code in ['internal','outgoing'] :

                            qty_rolls_origin = quant_origin.qty_rolls or 0
                            quant_origin.qty_rolls = qty_rolls_origin - line.qty_rolls










        return res

class PurchaseOrder(models.Model):
    _inherit       = 'purchase.order'


    def open_product_wizard_variant(self):
        return {
            "name": f"AGREGAR PRODUCTO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            #"view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "product.wizard.variant",
            #"res_id": self.id,
            "target": "new",
            "context": {
                'default_purchase_id': self.id
            }

        }

class PurchaseOrderLine(models.Model):
    _inherit       = 'purchase.order.line'
    qty_rolls = fields.Float(string="Rollos")



    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res.update({
            'qty_rolls': self.qty_rolls
        })
        return res