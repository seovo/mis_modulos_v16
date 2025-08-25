# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteFirstStockVariantController(WebsiteSaleVariantController):

    @route()
    def get_combination_info_website(self, *args, **kwargs):
        request.update_context(website_sale_stock_wishlist_get_wish=True)
        combination_info = super().get_combination_info_website(*args, **kwargs)

        #raise ValueError(combination_info)

        return combination_info

'''

import json
from odoo.http import request, route
from odoo.addons.website_sale.controllers import variant


class WebsiteSaleVariantController(variant.WebsiteSaleVariantController):

    @route('/website_sale/get_combination_info', type='json', auth='public', methods=['POST'], website=True)
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, parent_combination=None,
        **kwargs
    ):
        combination_info = super(WebsiteSaleVariantController, self).get_combination_info_website(
            product_template_id, product_id, combination, add_qty, parent_combination, **kwargs
        )

        raise ValueError(combination_info)

        return combination_info

'''

