# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
import json
import hashlib
from urllib.parse import urljoin
import time
from base64 import b64encode

STATUS_DETAILS = {
    '24': 'Paymentez Fraud - Refund requested.',
    '25': 'Invalid AuthCode - Refund requested.',
    '26': 'AuthCode expired - Refund requested.',
    '27': 'Merchant - Pending refund.',
    '20': 'Authorization code expired.',
    '21': 'Paymentez Fraud - Pending refund.',
    '22': 'Invalid AuthCode - Pending refund.',
    '23': 'AuthCode expired - Pending refund.',
    '28': 'Merchant - Refund requested.',
    '1': 'Verification required, please see Verification section.',
    '0': 'Waiting for Payment.',
    '3': 'Paid.',
    '7': 'Refund.',
    '6': 'Fraud.',
    '9': 'Rejected by carrier.',
    '8': 'Chargeback',
    '11': 'Paymentez fraud.',
    '10': 'System error.',
    '13': 'Time tolerance.',
    '12': 'Paymentez blacklist.',
    '19': 'Invalid Authorization Code.',
    '32': 'OTP successfully validated.',
    '31': 'Waiting for OTP.',
    '30': 'Transaction seated (only Datafast).',
    '34': 'Partial refund',
    '33': 'OTP not validated.'
}

STATUS_MAP = {
    0: 'pending',
    1: 'done',
    2: 'error',
    4: 'error'
}


class NuveiAPI():
    """
    Nuvei REST API integration.
    """
    def __init__(self, provider):
        """
        Initiate the environment with the acquirer data.
        """
        self.provider = provider.sudo()

    def _get_api_url(self):
        """
        Get correct api url based in acquirer enviroment
        """
        if self.provider.state == 'test':
            url = 'https://ccapi-stg.paymentez.com/'
        else:
            url = 'https://ccapi.paymentez.com/'
        return url

    def _provider_request(self, url, data, default_response):
        """
        Make a request to any api url
        """
        try:
            headers = {
                'Auth-Token': self._get_auth_request_data(),
                'content-type': "application/json"
            }
            response = requests.post(url, json=data, headers=headers)
            return json.loads(response.content)
        except Exception as e:
            default_response.update({'error': "Unexpected Error",
                                     'message': str(e)})
            return default_response

    def _get_auth_request_data(self):
        """
        Build auth token to make API requests
        """
        nuvei_server_application_code = self.provider.nuvei_server_app_code
        nuvei_server_app_key = self.provider.nuvei_server_app_key
        unix_timestamp = str(int(time.time()))
        uniq_token_string = '%s%s' % (nuvei_server_app_key, unix_timestamp)
        uniq_token_hash = hashlib.sha256(uniq_token_string.encode('utf-8')).hexdigest()
        token = '%s;%s;%s' % (nuvei_server_application_code, unix_timestamp, uniq_token_hash)
        auth_token = b64encode(bytes(token, 'utf-8'))
        return auth_token

    def _get_create_refund_data(self, transaction_id):
        """
        Returns basic data for Refund API request
        """
        request_values = {
            "transaction": {
                "id": transaction_id
            }
        }
        return request_values

    # Transaction refund management
    def create_refund(self, transaction_id):
        """
        Create a basic transaction with given token by a frontend
        """
        data = self._get_create_refund_data(transaction_id)
        default_response = {'status': 'failure', "detail": "Connection error"}
        request_url = 'v2/transaction/refund/'
        response = self._provider_request(urljoin(self._get_api_url(), request_url),
                                          data, default_response)
        return response

    def _get_verify_data(self, transaction_id, user_id, value):
        """
        Returns basic data for Refund API request
        """
        request_values = {
            "user": {
                "id": user_id
            },
            "transaction": {
                "id": transaction_id
            },
            "type": "BY_OTP",
            "value": value,
            "more_info": True

        }
        return request_values

    def verify(self, transaction_id, user_id, value):
        """
        Verify if inserted token is valid when OTP
        """
        data = self._get_verify_data(transaction_id, user_id, value)
        default_response = {'status': 'failure', "detail": "Connection error"}
        request_url = 'v2/transaction/verify/'
        response = self._provider_request(urljoin(self._get_api_url(), request_url),
                                          data, default_response)
        return response

    def validate_response(self, values):
        """
        Validate that response values comes from Nuvei and not from
        other site. If md5(transaction_id + app_code + user_id + app_key) is equal
        to stoken then response is valid.
        """
        transaction_id = values.get('transaction', {}).get('id', '')
        user_id = values.get('user', {}).get('id', '')
        stoken = values.get('transaction', {}).get('stoken', '')

        for_md5 = '%s_%s_%s_%s' % (
            transaction_id, self.provider.nuvei_client_app_code,
            user_id, self.provider.nuvei_client_app_key
        )
        local_stoken = hashlib.md5(for_md5).hexdigest()
        return local_stoken == stoken
