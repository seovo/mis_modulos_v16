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
    #checkout_code_combopay = fields.Char(
    #    string='Checkout Combopay Id',
    #    help='Checkout Combopay Id, useful to identify transaction.'
    #)


    def _get_specific_rendering_values(self, processing_values):





        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)

        order = self.sale_order_ids

        if not order.customer_order_delivery_date:
            raise ValueError('Se requiere fecha de envio')

        date_order = order.date_order.date()
        raise ValueError(date_order)

        return res

        if self.provider_code != 'mercadopagolink':
            return res


        link = None

        for line in self.sale_order_ids.order_line:
            if line.product_id.sale_ok and line.product_id.link_mercado_pago:
                link = line.product_id.link_mercado_pago

        if not  link:
            raise ValueError('No se Encontro Link de Pago')




        return {
            'api_url': link,
            #'headers': headers
            #'data': data,
        }


