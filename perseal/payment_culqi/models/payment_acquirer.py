# coding: utf-8

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# Force the API version to avoid breaking in case of update on Culqui side
# cf https://www.culqi.com/api/#/versionado
# changelog https://www.culqi.com/api/#/versionado
CULQUI_HEADERS = {'Culqui-Version': '2017-02-08'}


class PaymentAcquirerCulqui(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('culqi', 'Culqi')])
    culqi_secret_key = fields.Char(required_if_provider='culqi', groups='base.group_user')
    culqi_publishable_key = fields.Char(required_if_provider='culqi', groups='base.group_user')

    @api.model
    def _get_culqi_api_url_tok(self):
        return 'secure.culqi.com/v2'

    @api.model
    def _get_culqi_api_url(self):
        return 'api.culqi.com/v2'

    @api.model
    def culqi_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'cc_number': data['cc_number'],
            'cc_holder_name': data['cc_holder_name'],
            'cc_expiry': data['cc_expiry'],
            'cc_brand': data['cc_brand'],
            'cvc': data['cvc'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id'])
        })
        return payment_token

    def culqi_form_generate_values(self, tx_values):
        self.ensure_one()
        tx_values = dict(tx_values)
        temp_tx_values = {
            'company': self.company_id.name,
            'amount': tx_values['amount'],  # Mandatory
            'currency_id': tx_values['currency'].id,  # same here
            'currency_symbol': tx_values['currency'].symbol,
            'address_line1': tx_values.get('partner_address'),  # Any info of the partner is not mandatory
            'address_city': tx_values.get('partner_city'),
            'address_country': tx_values.get('partner_country') and tx_values.get('partner_country').name or '',
            'email': tx_values.get('partner_email'),
            'address_zip': tx_values.get('partner_zip'),
            'name': tx_values.get('partner_name'),
            'phone': tx_values.get('partner_phone'),
            'partner_id': tx_values.get('partner').id,
            'returndata': tx_values.get('return_url'),
        }
        tx_values.update(temp_tx_values)
        return tx_values

    def culqi_s2s_form_validate(self, data):
        self.ensure_one()

        # mandatory fields
        for field_name in ["cc_number", "cvc", "cc_holder_name", "cc_expiry", "cc_brand"]:
            if not data.get(field_name):
                return False
        return True

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super()._get_feature_support()
        res['tokenize'].append('stripe')
        return res


class PaymentTransactionCulqui(models.Model):
    _inherit = 'payment.transaction'

    def culqi_s2s_do_refund(self, **kwargs):
        self.ensure_one()
        self.state = 'refunding'
        result = self._create_stripe_refund()
        return self._culqi_s2s_validate_tree(result)

    @api.model
    def _culqi_form_get_tx_from_data(self, data):
        """ Given a data dict coming from stripe, verify it and find the related
        transaction record. """
        reference = data.get('reference')
        tx = self.search([('reference', '=', reference)])
        acq = self.env['payment.acquirer'].search([('name', '=', 'Culqi'), ('provider', '=', 'culqi')])
        tx._culqi_s2s_validate_tree(acq)
        return tx[0]

    def _culqi_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info('Culqi: trying to validate an already validated tx (ref %s)', self.reference)
            return True
        new_state = 'refunded' if self.state == 'refunding' else 'done'
        self.write({
            'state': new_state,
            'date_validate': fields.datetime.now(),
            'acquirer_reference': tree[0].id,
        })
        self.execute_callback()
        if self.payment_token_id:
            self.payment_token_id.verified = True
            return False

    def _culqi_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        reference = ['reference']
        if reference != self.reference:
            invalid_parameters.append(('Reference', reference, self.reference))
        return invalid_parameters

    def _culqi_form_validate(self, data):
        return self._culqi_s2s_validate_tree(data)
