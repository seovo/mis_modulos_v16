# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.http import request, route

from odoo.addons.website_sale.controllers import main
from odoo.http import request


class WebsiteSale(main.WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        values = super()._prepare_product_values(product, category, search, **kwargs)



        values['stock_warehouses'] = []



        #values['optional_product_ids'] = [p.with_context(active_id=p.id) for p in product.optional_product_ids]
        return values
