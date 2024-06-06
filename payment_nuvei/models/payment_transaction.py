# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_provider import ValidationError
from .nuvei_api import STATUS_DETAILS
from .nuvei_api import STATUS_MAP as API_STATUS_MAP
from datetime import datetime

from werkzeug import urls
from odoo.addons.payment import utils as payment_utils

STATUS_MAP = {'success': 'done', 'failure': 'error', 'pending': 'pending'}
STATE_MAP = {'test': 'test', 'enable': 'prod', 'disable': 'disable'}

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    authorization_code = fields.Char(
        string='Authorization code',
        help='Code returned by Nuvei, useful to identify transaction.'
    )
    provider_code = fields.Selection(
        string='Provider Code',
        related='provider_id.code',
        store=True,
        help='Technical field to hide fields added by Nuvei from '
             'Transaction form when provider is different than Nuvei.'
    )

    def _get_specific_rendering_values(self, processing_values):
        """
        Se hereda el metodo que devuelve los parametros para renderiar el formulario de
        redireccion.
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'nuvei':
            return res

        partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)

        nuvei_tx_values = {
            'tx_url': '/payment/nuvei/validate',
            'address1': self.partner_address,
            'amount': self.amount,
            'city': self.partner_city,
            'country': self.partner_country_id.code,
            'currency_code': self.currency_id.name,
            'email': self.partner_email,
            'first_name': partner_first_name,
            # 'handling': self.fees,
            'item_name': f"{self.company_id.name}: {self.reference}",
            'item_number': self.reference,
            'last_name': partner_last_name,
            'lc': self.partner_lang,
            'state': self.partner_state_id.name,
            'zip_code': self.partner_zip,
        }
        nuvei_tx_values.update({
            'nuvei_client_app_code': self.provider_id.nuvei_client_app_code,
            'nuvei_client_app_key': self.provider_id.nuvei_client_app_key,
            'environment': STATE_MAP.get(self.provider_id.state),
            'provider_id': self.provider_id.id,
            'provider_code': self.provider_id.code,
        })
        return nuvei_tx_values

    # @api.model
    # def _get_tx_from_feedback_data(self, provider, data):
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """
        Inherited method to get transaction with backend reference
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'nuvei':
            return tx

        reference = notification_data.get('reference', False) \
            or notification_data.get('transaction', {}).get('dev_reference', False)
        if self.env.context.get('only_get_transaction_reference'):
            return reference
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'nuvei')])
        if not tx:
            error_msg = _('Nuvei: received data with missing reference (%s)') % reference
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _process_notification_data(self, notification_data):
        """
        Manage payment returned data. Set transaction status and log important details.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'nuvei':
            return

        transaction_status = notification_data.get('transaction_status', '') or notification_data.get('transaction', {}).get('status', '')
        transaction_id = notification_data.get('transaction_id', '') or notification_data.get('transaction', {}).get('id', '')
        transaction_status_detail_code = notification_data.get('transaction_status_detail', '') \
            or notification_data.get('transaction', {}).get('status_detail', '')
        transaction_authorization_code = notification_data.get('transaction_authorization_code', '') \
            or notification_data.get('transaction', {}).get('transaction_authorization_code', '')
        transaction_status_detail = STATUS_DETAILS.get(str(transaction_status_detail_code), _('Invalid status detail'))

        former_tx_state = self.state
        txn_id = notification_data.get('bankOrderCode')
        self.provider_reference = txn_id
        if transaction_status == 'success':
            self._set_done(state_message=_('Validated Nuvei payment for tx %s: set as done') % (self.provider_reference))
            if self.state != former_tx_state:
                _logger.info('Validated Nuvei payment for tx %s: set as done' % (self.provider_reference))
            else:
                _logger.info('Trying to update tx %s: as done but tx already is in that state' % (self.provider_reference))
        elif transaction_status == 'pending':
            self._set_pending(state_message=_('Transaction set as pending by nuvei, we need to wait to confirm your order.'))
            if self.state != former_tx_state:
                _logger.info('Validated nuvei payment for tx %s: set as pending' % (self.provider_reference))
            else:
                _logger.info('Trying to update tx %s: as pending but tx already is in that state' % (self.provider_reference))
        elif transaction_status == 'failure':
            error = 'Received error status for nuvei payment %s: %s, set as error' % (self.provider_reference, transaction_status)
            self._set_error(state_message=error)
            if self.state != former_tx_state:
                _logger.info(error)
            else:
                _logger.info('Trying to update tx %s: as error but tx already is in that state' % (self.provider_reference))
        else:
            error = 'Received unrecognized transaction_status for nuvei payment %s: %s, set as cancel' % (self.reference, transaction_status)
            self._set_cancel(state_message=error)
            if self.state != former_tx_state:
                _logger.info(error)
            else:
                _logger.info('Trying to update tx %s: as cancel but tx already is in that state' % (self.provider_reference))
        res = {
            'provider_reference': transaction_id,
            'authorization_code': transaction_authorization_code,
            'state_message': '\n'.join([self.state_message or '', transaction_status_detail])
        }

        return self.write(res)
