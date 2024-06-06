# -*- coding: utf-8 -*-

from odoo import http, api
from odoo.addons.payment.models.payment_provider import ValidationError
from odoo.http import request
from odoo.addons.payment_nuvei.models.nuvei_api import NuveiAPI

import logging
import pprint
from datetime import datetime

_logger = logging.getLogger(__name__)


class NuveiController(http.Controller):

    @http.route('/payment/nuvei/validate', type='http', auth="public", website=True)
    def NuveiValidate(self, **post):
        """
        Manage nuvei transaction status. Redirect to status poll when payment was correct.
        """
        arg = {
            'transaction_message': 'Start /payment/nuvei/validate',
            'reference': request.env['payment.transaction'].with_context(
                only_get_transaction_reference=True
            )._get_tx_from_notification_data('nuvei', post)
        }
        self.update_transaction_message(**arg)
        try:
            arg = {
                'transaction_message': 'Go to payment _handle_notification_data',
                'reference': request.env['payment.transaction'].with_context(
                    only_get_transaction_reference=True
                )._get_tx_from_notification_data('nuvei', post)
            }
            self.update_transaction_message(**arg)
            request.env['payment.transaction'].sudo()._handle_notification_data('nuvei', post)
        except ValidationError as e:
            arg = {
                'transaction_message': 'Unable to validate the nuvei payment: %s' % e,
                'reference': request.env['payment.transaction'].with_context(
                    only_get_transaction_reference=True
                )._get_tx_from_notification_data('nuvei', post)
            }
            self.update_transaction_message(**arg)
            _logger.exception('Unable to validate the nuvei payment')
        return request.redirect('/payment/status')

    @http.route('/payment/nuvei/ipn/', type='http', auth='none', methods=['POST'], csrf=False)
    def paymentez_ipn(self, **post):
        """
        Manage asynchronous payment status notification. Search transation
        by reference and run form feedback.
        """
        _logger.info('Beginning Nuvei _handle_notification_data with post data %s', pprint.pformat(post))
        arg = {'transaction_message': 'Start /payment/nuvei/ipn/ with data %s' % pprint.pformat(post),
               'provider_reference': post.get('transaction', {}).get('id', ''),
               }
        self.update_transaction_message(**arg)
        transaction_id = post.get('transaction', {}).get('id', '')
        if transaction_id:
            tx = request.env['payment.transaction'].search([('provider_reference', '=', transaction_id)], limit=1)
            if tx:
                if tx.state in ('done', 'cancel'):
                    arg = {'transaction_message': 'Transaction_id already received',
                           'provider_reference': post.get('transaction', {}).get('id', ''),
                           }
                    self.update_transaction_message(**arg)
                    # transaction_id already received
                    return http.Response(status=204)
                NuveiAPI(tx.provider_id)
                # Validate that post response is a valid placetopay response
                if api.validate_response(post):
                    arg = {'transaction_message': 'Start _handle_notification_data',
                           'provider_reference': post.get('transaction', {}).get('id', ''),
                           }
                    self.update_transaction_message(**arg)
                    # If response is valid make form feeedback
                    request.env['payment.transaction'].sudo()._handle_notification_data('nuvei', post)
                    # success
                    return http.Response(status=200)
                else:
                    arg = {'transaction_message': 'Nuvei: Response verification fail.',
                           'provider_reference': post.get('transaction', {}).get('id', ''),
                           }
                    self.update_transaction_message(**arg)
                    _logger.warning('Nuvei: Response verification fail.')
                    # token error
                    return http.Response(status=203)
            else:
                _logger.warning('Nuvei: Transaction not found using reference from response.')
                # token error
                return http.Response(status=203)
        else:
            _logger.warning('Nuvei: Invalid response data.')
            # token error
            return http.Response(status=203)

    @http.route(['/payment/nuvei/get_submit_data'], type='json', auth="public", website=True)
    def get_submit_data(self, **kwargs):
        """
        Get some data needed to make submit to payment provider.
        We need user data and order data
        """
        if kwargs.get('order_id', False):
            order = request.env['sale.order'].sudo().browse(int(kwargs.get('order_id')))
        else:
            order = request.website.sale_get_order()

        if kwargs.get('invoice_id', False):
            invoice = request.env['account.move'].sudo().browse(int(kwargs.get('invoice_id')))

        user_fields = kwargs.get('user_fields', [])
        order_fields = kwargs.get('order_fields', [])
        user_data = request.env.user.read(user_fields)[0]
        if len(order) > 0:
            order_data = order.read(order_fields)[0] if order else {}
            error = len(order.transaction_ids.filtered(lambda t: t.state == 'done')) > 0
        elif kwargs.get('invoice_id', False):
            order_data = invoice.read(order_fields)[0] if invoice else {}
            error = len(invoice.transaction_ids.filtered(lambda t: t.state == 'done')) > 0

        return {'user_data': user_data, 'order_data': order_data, 'error': error}

    @http.route(['/payment/nuvei/update_transaction_message'], type='json', auth="public", website=True)
    def update_transaction_message(self, **kwargs):
        """
        Actualiza el mensaje de la transaccion con el objetivo de llevar
        un registro de las acciones que realizamos.
        """
        message = kwargs.get('transaction_message', '')
        reference = kwargs.get('reference', '')
        reference_field = 'reference'
        if not reference:
            reference = kwargs.get('provider_reference', '')
            reference_field = 'provider_reference'

        tx = request.env['payment.transaction'].sudo().search([(reference_field, '=', reference)], limit=1)
        if tx:
            message = '%s INFO %s' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
            tx.state_message = '\n'.join([tx.state_message or '', message])
            return True
        else:
            return False
