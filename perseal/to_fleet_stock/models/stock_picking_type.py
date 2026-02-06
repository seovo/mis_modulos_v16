# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('fleet_consumption', 'Fleet Consumption')], ondelete={'fleet_consumption': 'cascade'})