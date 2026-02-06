# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    down_payment_product_id = fields.Many2one(
        'product.product',
        'Producto anticipo de pago',
        domain="[('type', '=', 'service')]",
        readonly=False,
        config_parameter='l10n_pe_down_payments_edi.down_payment_product_id',
        help='Default product used for payment advances')