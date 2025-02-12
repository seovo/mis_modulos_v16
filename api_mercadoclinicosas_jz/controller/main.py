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
from odoo.exceptions import AccessError
import odoo

class ApiClinicos(http.Controller):

    @http.route(['/apiclinicos/validate_login'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def index_validate_login(self, **post):
        redirect = None
        values = {}

        return  request.session.authenticate(request.db, request.params['login'], request.params['password'])

        try:
            uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
            values.update({
                'login_success': True
            })
            #request.params['login_success'] = True
            #return request.redirect(self._login_redirect(uid, redirect=redirect))
        except odoo.exceptions.AccessDenied as e:
            if e.args == odoo.exceptions.AccessDenied().args:
                values.update({
                    'error': "Incorrecto usuario/contraseña"
                })
                #values['error'] = _("Wrong login/password")
            else:
                values.update({
                    'error': e.args[0]
                })
                #values['error'] = e.args[0]

        return values

    @http.route('/apiclinicos/websites', type="json", auth='public',
                website=True, methods=['POST', 'GET'], csrf=False, save_session=False)
    def mercadopagolink_payment_response(self, **data):
        websites = request.env['website'].sudo().search([])
        data = []
        for website in websites:


            if website.company_id.country_id:
                #ir.config_parameter
                url_base = request.env['ir.config_parameter'].sudo().search([('key','=','web.base.url')])
                img_country = f'''{url_base.value}{website.company_id.country_id.image_url}'''
                data.append({
                    'id': website.id,
                    'name': website.display_name,
                    'country_name': website.company_id.country_id.name ,
                    'country_image': img_country

                })

        return {'websites': data}






