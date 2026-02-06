# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    order_ref_in_invoice = fields.Boolean(string='Nº Orden en Factura')