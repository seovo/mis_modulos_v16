import logging
import pprint
from odoo import http
from odoo.http import request
import ast

_logger = logging.getLogger(__name__)

class PaymentRecurrenteController(http.Controller):
    @http.route('/payment/recurrente/response', type='http', auth='public',
                website=True, methods=['POST','GET'], csrf=False, save_session=False)
    def recurrente_payment_response(self, **data):
        _logger.info("Received Recurrente return data:\n%s",
                     pprint.pformat(data))

        #checkout_id = data.get('checkout_id')
        tx_sudo = request.env[
            'payment.transaction'].sudo()._get_tx_from_notification_data(
            'recurrente', data)
        tx_sudo._handle_notification_data('recurrente', data)
        return request.redirect('/payment/status')