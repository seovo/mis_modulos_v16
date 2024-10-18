# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models , api

#from odoo.addons.payment_paypal import const


_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('recurrente', "Recurrente")], ondelete={'recurrente': 'set default'}
    )
    #'''
    recurrente_public_key = fields.Char(
        'Public Key',
        groups='base.group_user',
        required_if_provider='recurrente',
        help="Public Key credentials provied by recurrente"
    )
    recurrente_secret_key = fields.Char(
        'Secret Key',
        groups='base.group_user',
        required_if_provider='recurrente',
        help="Secret Key credentials provied by recurrente"
    )

    '''
    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'recurrente':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES
    '''
    @api.model
    def _get_payment_method_information(self):
        """ Override method to add MyFatoorah payment method information."""
        res = super()._get_payment_method_information()
        res['recurrente'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    def _get_redirect_form_view(self, is_validation=False):
        res = super()._get_redirect_form_view(is_validation)
        _logger.exception(f'Porque! : {res}')
        return res

    #'''

    '''
    paypal_email_account = fields.Char(
        string="Email",
        help="The public business email solely used to identify the account with PayPal",
        required_if_provider='paypal',
        default=lambda self: self.env.company.email,
    )
    paypal_pdt_token = fields.Char(string="PDT Identity Token", groups='base.group_system')

    #=== BUSINESS METHODS ===#

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'paypal':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _paypal_get_api_url(self):
        """ Return the API URL according to the provider state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        if self.state == 'enabled':
            return 'https://www.paypal.com/cgi-bin/webscr'
        else:
            return 'https://www.sandbox.paypal.com/cgi-bin/webscr'

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'paypal':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES
    '''