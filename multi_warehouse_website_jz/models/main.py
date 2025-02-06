from odoo.addons.payment.controllers import portal as payment_portal
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request, route
from werkzeug.exceptions import Forbidden, NotFound
from odoo.tools import lazy, str2bool
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.http_routing.models.ir_http import slug
import logging
from odoo.exceptions import AccessError, MissingError, ValidationError
_logger = logging.getLogger(__name__)
import base64

class WebsiteSale(payment_portal.PaymentPortal):
    @http.route([
        '/set_warehouse_session/<model("stock.warehouse"):warehouse>',
    ], type='http', auth="public", website=True)
    def set_warehouse_session(self,  warehouse, **post):
        request.session['active_warehouse_id'] = int(warehouse)
        #raise ValidationError(request.session['active_warehouse_id'])
        return request.redirect('/')