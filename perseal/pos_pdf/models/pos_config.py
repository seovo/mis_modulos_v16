# -*- coding: utf-8 -*-

from odoo import fields, models, _

types_list = ['char', 'date', 'datetime', 'integer', 'float', 'selection', 'text', 'boolean']


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    # Campo que define si se mostrará o no el código QR en el ticket de venta
    include_qr_code = fields.Boolean(string='Include QR Code in Sale Ticket', help='If this checked, then QR Code displayed on Sale Ticket.')
