# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

#from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
#from odoo.addons.payment_paypal.const import PAYMENT_STATUS_MAPPING


_logger = logging.getLogger(__name__)

import requests
import json


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to return Stripe-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'recurrente' or self.operation == 'online_token':
            return res

        #intent = self._stripe_create_intent()
        #base_url = self.provider_id.get_base_url()
        return {
            #'client_secret': intent['client_secret'],
            #'return_url': url_join(
            #    base_url,
            #    f'{StripeController._return_url}?{url_encode({"reference": self.reference})}',
            #),
            'return_url': 'xdd'
        }


    def send_payment_recurrente(self):
        #base_api_url = self.env['payment.provider'].search([('code', '=', 'myfatoorah')])._myfatoorah_get_api_url()
        api_url = 'https://app.recurrente.com/api/checkouts/'
        odoo_base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        provider = self.provider_id
        sale_order = self.sale_order_ids
        #currency = self.env.company.currency_id.name

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-PUBLIC-KEY':  provider.recurrente_public_key ,
            'X-SECRET-KEY': provider.recurrente_secret_key,
            #'Authorization': f'Bearer {api_key}',
        }

        items = []

        for line in sale_order.order_line:
            if line.product_id and line.price_total != 0:
                items.append({
                    'name': line.name ,
                    'currency': "GTQ" ,
                    "amount_in_cents": int(line.price_unit)  ,
                    "quantity": int(line.product_uom_qty)

                })


        data = {
            "items": items ,
            "success_url": odoo_base_url ,
            "cancel_url": odoo_base_url,
            #"user_id": "us_123456",
            #"metadata": {}
        }

        _logger.info(
            "Recurrente data %s",
            data, self.reference
        )

        payload = json.dumps(data)

        _logger.info(
            "Recurrente Payload data %s",
            data, api_url
        )
        response = requests.request("POST", api_url, headers=headers,
                                    data=payload)

        response_data = response.json()

        if response_data.get('id') and response_data.get('checkout_url') :
            return {
                'api_url': response_data.get('checkout_url'),
                'data': data,
            }


        else:
            validation_errors = str(response_data)
            raise ValidationError(f"RESPONSE DATA RECUURENTE : {validation_errors}")


    def _get_specific_rendering_values(self, processing_values):

        _logger.exception('Recurrente : _get_specific_rendering_values')
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'recurrente':
            return res
        return self.send_payment_recurrente()




    def _get_tx_from_notification_data(self, provider_code, notification_data):
        _logger.exception('Habersh2')
        """ Override of payment to find the transaction based on Paypal data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'recurrente' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'recurrente')])
        if not tx:
            raise ValidationError(
                "Recurrente: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    '''
    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Paypal data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'paypal':
            return

        if not notification_data:
            self._set_canceled(_("The customer left the payment page."))
            return

        # Update the provider reference.
        txn_id = notification_data.get('txn_id')
        txn_type = notification_data.get('txn_type')
        if not all((txn_id, txn_type)):
            raise ValidationError(
                "PayPal: " + _(
                    "Missing value for txn_id (%(txn_id)s) or txn_type (%(txn_type)s).",
                    txn_id=txn_id, txn_type=txn_type
                )
            )
        self.provider_reference = txn_id
        self.paypal_type = txn_type

        # Force PayPal as the payment method if it exists.
        self.payment_method_id = self.env['payment.method'].search(
            [('code', '=', 'paypal')], limit=1
        ) or self.payment_method_id

        # Update the payment state.
        payment_status = notification_data.get('payment_status')

        if payment_status in PAYMENT_STATUS_MAPPING['pending']:
            self._set_pending(state_message=notification_data.get('pending_reason'))
        elif payment_status in PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled()
        else:
            _logger.info(
                "received data with invalid payment status (%s) for transaction with reference %s",
                payment_status, self.reference
            )
            self._set_error(
                "PayPal: " + _("Received data with invalid payment status: %s", payment_status)
            )
    '''