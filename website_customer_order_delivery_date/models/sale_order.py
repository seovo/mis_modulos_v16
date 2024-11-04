# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class sale_order(models.Model):

    """Adds the fields for options of the customer order delivery"""

    _inherit = "sale.order"
    _description = 'Sale Order'

    customer_order_delivery_date = fields.Date(string='Delivery Date')
    customer_order_delivery_comment = fields.Text(string='Delivery Comment', translate=True)
