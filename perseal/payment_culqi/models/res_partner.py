from copy import deepcopy
from culqi.client import Culqi
from culqi.resources import Token
from culqi.resources import Charge

import logging

from odoo import models, api, _

__version__ = ".".join(("1", "0", "3"))

_logger = logging.getLogger(__name__)


class ResPartnerVat(models.Model):
    _inherit = 'res.partner'

    def generate_token(self, data):

        pub_k = data.get('public_k')
        prv_k = data.get('private_k')
        data.pop('public_k')
        data.pop('private_k')

        self.version = __version__
        self.public_key = pub_k
        self.private_key = prv_k
        self.culqi = Culqi(self.public_key, self.private_key)
        self.token = Token(client=self.culqi)

        self.token_data = deepcopy(data)
        self.metadata = {"order_id": "0001"}
        token = self.token.create(data=self.token_data)
        if token["data"]["object"] == "token" and token.get('status') == 201:
            acquirer = self.env['payment.acquirer'].search([('name', '=', 'Custom')])
            obj = {'name': token["data"]["card_number"],
                   'verified': token["data"]["active"],
                   'acquirer_ref': token["data"]["id"],
                   'active': token["data"]["active"],
                   'partner_id': self.id,
                   'acquirer_id': acquirer.id}
            return {'status': 201, 'token': token["data"]["id"], 'card_number': token['data']['card_number']}
        else:
            return {'status': token.get('status'), 'user_message': token["data"]["user_message"]}
        return False

    def generate_chargue(self, tokn, data):
        self.version = __version__

        stripe_key = data['stripe_key']
        stripe_secret_key = data['stripe_secret_key']

        self.culqi = Culqi(stripe_key, stripe_secret_key)

        data.pop('stripe_key')
        data.pop('stripe_secret_key')

        self.charge = Charge(client=self.culqi)

        charge_data = {
            "amount": False,
            "capture": False,
            "currency_code": data["currency_code"],
            "description": data["description"],
            "email": data["email"],
            "installments": 0,
            "source_id": tokn}

        # charge_data["source_id"] = tokn

        charge_data["amount"] = int(data["amount"] * 100)
        # charge_data["amount"] = 1000
        # charge_data['description'] = data['description']
        charge = self.charge.create(data=charge_data)
        # charge = {'status':201}
        charge['reference'] = data["description"]

        return charge

    def btn_generate_token(self, context=None):
        TOKEN = {
            "cvv": "123",
            "card_number": "4111111111111111",
            "expiration_year": "2020",
            "expiration_month": "09",
            "email": "richard@piedpiper.com",
        }
        tokn = self.generate_token(TOKEN)
        return tokn

    @api.model
    def btn_generate_token2(self, id, obj):

        TOKEN = {
            "cvv": "123",
            "card_number": "4111111111111111",
            "expiration_year": "2020",
            "expiration_month": "09",
            "email": "richard@piedpiper.com",
        }
        tokn = self.browse(id).generate_token(obj)
        return tokn
