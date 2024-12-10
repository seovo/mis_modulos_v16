import logging
import pprint
from odoo import http
from odoo.http import request
from odoo import _, fields, models
from datetime import datetime, timedelta

from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.tools import lazy, str2bool
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

_logger = logging.getLogger(__name__)

class PaymentMercadoPago(http.Controller):

    @http.route('/payment/status/mercadopagolink', type='http', auth='public',
                website=True, methods=['POST', 'GET'], csrf=False, save_session=False)
    def mercadopagolink_payment_response(self, **data):
        date_start = fields.Datetime().now() -  timedelta(days=2)
        request.env['vex.synchro'].sudo().start_sync_sale_mercadopago(date_start=date_start)
        try:
            request.env['vex.synchro'].sudo().start_sync_sale_mercadopago(date_start=date_start)
        except:
            pass

        return request.redirect('/payment/status')
