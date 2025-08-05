from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    def _get_specific_rendering_values(self, processing_values):

        if self.sale_order_ids.carrier_id.is_store_pick and not self.sale_order_ids.sucursal_toy_id:
            raise ValidationError('Seleccione una sucursal')
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)

        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    sucursal_toy_id = fields.Many2one('sucursales.toys',string="Sucursal")

    def verify_seguidores_sucursal(self):

        if self.carrier_id.is_store_pick and not self.sucursal_toy_id:
            raise ValidationError('Seleccione una sucursal')

        if self.sucursal_toy_id:
            parterns = self.message_partner_ids
            for user in self.sucursal_toy_id.user_notify_ids:
                if user.partner_id.id not in parterns.ids:
                    self.message_partner_ids = [(4,user.partner_id.id)]

    def write(self,vals):
        res = super().write(vals)
        if 'state' in vals:
            if self.state in ['sale','sent']:
                self.verify_seguidores_sucursal()

        return res

    def action_confirm(self):
        self.verify_seguidores_sucursal()

        res = super().action_confirm()
        return res


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    is_store_pick = fields.Boolean(string='Entregar en Tienda',
                                   help="Enable this to identify this as an "
                                        "In-store PickUp delivery method")
    store_ids = fields.Many2many('sucursales.toys',
                                 string="Available Stores",
                                 help="Choose the stores available for "
                                      "in-store picking and if no stores "
                                      "implies all stores are available")
