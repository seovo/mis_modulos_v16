# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CulqiController(http.Controller):


    @http.route(['/payment/culqi/create_charge'], type='json', auth='public')
    def culqi_create_charge(self, **post):
        """ Create a payment transaction

        Expects the result from the user input from checkout.js popup"""
        TX = request.env['payment.transaction']
        tx = None
        if post.get('tx_ref'):
            tx = TX.sudo().search([('reference', '=', post['tx_ref'])])
        if not tx:
            tx_id = (post.get('tx_id') or request.session.get('sale_transaction_id') or
                     request.session.get('website_payment_tx_id'))
            tx = TX.sudo().browse(int(tx_id))
        if not tx:
            raise werkzeug.exceptions.NotFound()

        culqi_token = post['token']
        amount = post['amount']
        invoice_num = post['invoice_num']
        card_number = post['card_number']
        

        response = None
        charge_data = {
            "amount": tx.amount,
            "capture": False,
            "currency_code": tx.currency_id.name,
            "description": invoice_num,
            "email": post['email'],
            "installments": 0,
            "source_id": None,
            'stripe_key':post['stripe_key'],
            'stripe_secret_key':post['stripe_secret_key']
           }
        if tx.type == 'form_save' and tx.partner_id:
            payment_token_id = request.env['payment.token'].sudo().create({
                'acquirer_id': tx.acquirer_id.id,
                'partner_id': tx.partner_id.id,
                'stripe_token': culqi_token,
                'acquirer_ref': 9,
                'name':card_number
            })
            



            tx.payment_token_id = payment_token_id
            chargue = tx.partner_id.generate_chargue(culqi_token, charge_data)
        else:
            chargue = tx.partner_id.generate_chargue(culqi_token, charge_data)
        _logger.info('Culqi: entering form_feedback with post data %s', pprint.pformat(chargue))
        if chargue['status'] == 201:
            request.env['payment.transaction'].sudo().with_context(lang=None).form_feedback(chargue, 'culqi')
            tx.sudo().write({'acquirer_reference':chargue['data']['id']})
            post['merchant_message'] = 'ok'
        
        else:
            post['merchant_message'] = chargue['data']['merchant_message']
        post['return_url'] = '/shop/payment/validate'
        post['transaction_id'] = tx.id
        post['status'] = chargue['status']
        

        
        return post


