# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('nuvei', 'nuvei')], ondelete={'nuvei': 'set default'})
    nuvei_client_app_code = fields.Char(
        'Client APP Code',
        groups='base.group_user',
        required_if_provider='nuvei',
        help="Client credentials provied by Nuvei"
    )
    nuvei_client_app_key = fields.Char(
        'Client APP Key',
        groups='base.group_user',
        required_if_provider='paymentez',
        help="Client credentials provied by Paymentez"
    )
    nuvei_server_app_code = fields.Char(
        'Server APP Code',
        groups='base.group_user',
        required_if_provider='paymentez',
        help="Server credentials provied by Paymentez"
    )
    nuvei_server_app_key = fields.Char(
        'Server APP Key',
        groups='base.group_user',
        required_if_provider='paymentez',
        help="Server credentials provied by Paymentez"
    )

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """
        Override of payment to unlist Nuvei providers when the currency is not supported.
        """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        nuvei_provider_ids = providers.filtered(lambda a: a.code == 'nuvei')
        for nuvei_provider in nuvei_provider_ids:
            if currency and currency != (
                nuvei_provider.journal_id.currency_id
                or nuvei_provider.journal_id.company_id.currency_id
            ):
                providers = providers - nuvei_provider
        return providers

    # def _get_default_payment_method_id(self):
    #     """
    #     Returns preferred payment method for this provider.
    #     """
    #     self.ensure_one()
    #     if self.code != 'nuvei':
    #         return super()._get_default_payment_method_id()
    #     return self.env.ref('payment_nuvei.payment_method_nuvei').id