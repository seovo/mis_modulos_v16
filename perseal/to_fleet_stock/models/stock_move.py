# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    fleet_service_type_id = fields.Many2one('fleet.service.type', related='picking_id.fleet_service_type_id', store=True,
                                            help="The service type of the fleet related to this stock move")

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', help="This is to indicate that this move concerns a vehicle")

    @api.model
    def _get_vehicle_cost_location_type(self):
        return ['production', 'inventory']

    @api.model
    def _prepare_vehicle_cost_data(self):
        date = fields.Date.from_string(self.date)
        amount = self.product_id.standard_price * self.quantity
        res = {
            'vehicle_id': self.vehicle_id.id,
            'description': self.fleet_service_type_id.name or '' + ' ' + self.vehicle_id.name,
            'date': fields.Date.to_string(date),
            'amount': abs(amount),
            'created_from_stock_move_id': self.id,
            }

        cost_type = ''
        if self.fleet_service_type_id:
            res['service_type_id'] = self.fleet_service_type_id.id

        #     fuel_type_id = self.env.ref('fleet.type_service_service_8')
        #     if fuel_type_id and fuel_type_id.id == self.fleet_service_type_id.id:
        #         cost_type = 'fuel'
        #     elif self.fleet_service_type_id.category == 'service':
        #         cost_type = 'services'
        #     elif self.fleet_service_type_id.category == 'contract':
        #         cost_type = 'contract'
        # if cost_type:
        #     res['cost_type'] = cost_type

        return res

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

        FleetVehicleCost = self.env['fleet.vehicle.log.services']
        if not self.env.user.has_group('fleet.fleet_group_user'):
            FleetVehicleCost = FleetVehicleCost.sudo()

        for r in self:
            if r.vehicle_id and r.location_dest_id.usage in r._get_vehicle_cost_location_type():
                cost_id = FleetVehicleCost.create(r._prepare_vehicle_cost_data())

        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', help="This is to indicate that this move concerns a vehicle")