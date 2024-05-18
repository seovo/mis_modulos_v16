# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.http import request, route

from odoo.addons.website_sale.controllers import main
from odoo.http import request


class WebsiteSale(main.WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        values = super()._prepare_product_values(product, category, search, **kwargs)

        '''
        stock_locations = {

        }

        #raise ValueError(product)

        domain = [("location_id.usage", "in", ["internal", "transit"]),('product_id.product_tmpl_id','=',product.id)]

        quants = request.env["stock.quant"].sudo().search(domain)

        if quants:
            for quant in quants:

                if quant.location_id.warehouse_id.id in stock_locations:
                    stock_locations.update({
                         quant.location_id.warehouse_id.id :  {
                            'warehouse': quant.location_id.warehouse_id.display_name ,
                            'stock': quant.quantity + stock_locations[quant.location_id.warehouse_id.id]['stock']
                         }
                    })
                else:
                    stock_locations.update({
                        quant.location_id.warehouse_id.id: {

                            'warehouse': quant.location_id.warehouse_id.display_name,
                            'stock': quant.quantity
                        }
                    })

        res_locations = []

        for data in stock_locations:
            res_locations.append(stock_locations[data])
            
        '''

        values['stock_warehouses'] = []



        #values['optional_product_ids'] = [p.with_context(active_id=p.id) for p in product.optional_product_ids]
        return values
