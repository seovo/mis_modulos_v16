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
from odoo.addons.payment.controllers import portal as payment_portal

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools import lazy, str2bool
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo import fields, http, SUPERUSER_ID, tools, _
import json  # Asegúrate de importar el módulo json
import requests


class ApiClinicos(http.Controller):

    @http.route(['/api/v1/detect/example'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False,cors='*')
    def apicamara_conectsenx(self, **post):
        data = http.request.httprequest.get_json()

        isActive = True

        url = f'http://34.171.72.80:8005/api/v1/detect/binarys?draw_result={isActive}'

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        res = requests.post(url, json=data, headers=headers)

        return res.json()


    @http.route(['/api/v1/detect/binarys'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False,cors='*')
    def apicamara_conectsen(self, **post):
        data = http.request.httprequest.get_json()
        isActive = True

        url = f'http://34.171.72.80:8005/api/v1/detect/binarys?draw_result={isActive}'

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        res = requests.post(url, json=data, headers=headers)

        return res




        return data

        #values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}

        #partner = request.env['res.partner'].sudo().create({
        #    'name':
        #})

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


