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



