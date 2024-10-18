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


    @api.model
    def _get_payment_method_information(self):
        """ Override method to add MyFatoorah payment method information."""
        res = super()._get_payment_method_information()
        res['recurrente'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    def sync_suscripciones_recurrente(self):
        return


