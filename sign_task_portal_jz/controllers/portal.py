# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(payment_portal.PaymentPortal):
    @http.route(['/my/tasks/<int:task_id>/accept'], type='json', auth="public", website=True)
    def task_sigm(self, task_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        #try:
        #    order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        #except (AccessError, MissingError):
        #    return {'error': _('Invalid order.')}

        #if not order_sudo._has_to_be_signed():
        #    return {'error': _('The order is not in a state requiring customer signature.')}
        #if not signature:
        #    return {'error': _('Signature is missing.')}

        order_sudo = request.env['project.task'].sudo().search([('id','=',int(task_id))])

        try:
            order_sudo.write({
                #'signed_by': name,
                #'signed_on': fields.Datetime.now(),
                'x_studio_firma_de_conformidad': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        #if not order_sudo._has_to_be_paid():
        #    order_sudo.action_confirm()
        #    order_sudo._send_order_confirmation_mail()

        #pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [order_sudo.id])[
        #    0]

        _message_post_helper(
            'project.task',
            order_sudo.id,
            _('Firmado por %s', name),
            #attachments=[('%s.pdf' % order_sudo.name, pdf)],
            token=access_token,
        )

        query_string = '&message=sign_ok'
        #if order_sudo._has_to_be_paid():
        #    query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }