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
import uuid


class ApiClinicos(http.Controller):



    @http.route(['/apiclinicos/signup'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def apiclinicos_signup(self, **post):
        #db = http.request.env.cr.dbname
        data = http.request.httprequest.get_json()

        #values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}


        values = {
            'name': data['name'] ,
            'email':  data['email'] ,
            'login': data['email'],
            'password': data['password'] ,
            'lang': 'es_AR'
        }

        #if not values:
        #    raise UserError(_("The form was not properly filled in."))

        ########

        login, password = request.env['res.users'].sudo().signup(values)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        pre_uid = request.session.authenticate(request.db, login, password)
        if not pre_uid:
            return False
            #raise SignupError(_('Authentication Failed.'))

        return True

    @http.route(['/apiclinicos/inactive/uuid/<string:token>'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def apiclinicos_inactive_uuid(self, token, **post):
        exist = request.env['clinicos.web.services'].sudo().search([('token', '=', token)])

        if exist:
            exist.active = False
            return True
        else:
            return False


    @http.route(['/apiclinicos/validate/uuid/<string:token>'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def apiclinicos_validate_uuid(self, token , **post):
        exist = request.env['clinicos.web.services'].sudo().search([('token','=',token)])

        if exist:
            return True
        else:
            return False

    @http.route(['/apiclinicos/login'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def apiclinicos_validate_login(self, **post):

        db = http.request.env.cr.dbname

        data = http.request.httprequest.get_json()


        values = {}


        try:
            uid = request.session.authenticate(db, data['login'], data['password'])
            values.update({
                'login_success': True ,
                'uid': uid
            })

            #generar codigo token uid

            unique_id = str(uuid.uuid4())  # Genera un UUID único

            request.env['clinicos.web.services'].sudo().create({
                'name': unique_id ,
                'token': unique_id
            })

            values.update({'uuid': unique_id})



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






