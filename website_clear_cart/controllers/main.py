# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsiteSaleClearCart(http.Controller):
    @http.route(['/shop/clear_cart'], type='json', auth="public", website=True)
    def clear_cart(self, **post):
        order = request.website.sale_get_order()
        if order:
            order.website_order_line.unlink()
