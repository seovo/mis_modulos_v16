from odoo import api, fields, models

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    is_fictic_warehouse = fields.Boolean(string="Operacion Check List")


class StockMove(models.Model):
    _inherit = 'stock.move'
    #date_event_install = fields.Datetime(string='Fecha Instalación')
    #date_event_install_end = fields.Datetime(string='Fecha Fin Instalación')
    #date_event_uninstall = fields.Datetime(string='Fecha Desistalación')
    #date_event_uninstall_end = fields.Datetime(string='Fecha Fin Desistalación')



class StockPicking(models.Model):
    _name = 'stock.picking'
    sale_event_id = fields.Many2one('sale.order')
    _inherit = ['portal.mixin', 'stock.picking']

    def action_assign(self):
        res = super().action_assign()

        if self.picking_type_id.is_fictic_warehouse:
            for line in self.move_ids_without_package:
                line.quantity = line.product_uom_qty

        return res

    def button_validate(self):

        if self.picking_type_id.is_fictic_warehouse:
            for line in self.move_ids_without_package:
                line.quantity = line.product_uom_qty


        res = super().button_validate()

        if self.picking_type_id.is_fictic_warehouse:
            for line in self.move_ids_without_package:
                line.quantity = line.product_uom_qty
                if line.product_id:
                    quant = self.env['stock.quant'].search([('location_id','=',self.location_id.id),('product_id','=',line.product_id.id)])

                    if quant:
                        quant.inventory_quantity = 0
                        quant.action_apply_inventory()




        return res

    @api.model
    def create(self,vals):
        #raise ValueError(vals)
        res = super().create(vals)
        return res


    # portal.mixin override
    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/my/checklist/{order.id}'


    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        #return {id: 1}
        return self.env.ref('sale.action_quotations_with_onboarding')

