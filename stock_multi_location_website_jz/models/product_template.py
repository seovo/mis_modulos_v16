from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name    = 'product.template'

    def _get_combination_info(
            self, combination=False, product_id=False, add_qty=1.0,
            parent_combination=False, only_template=False,
    ):
        res = super()._get_combination_info(
            combination, product_id, add_qty ,
            parent_combination, only_template,
        )

        if combination:
            domain = [("location_id.usage", "in", ["internal", "transit"]),
                      ("location_id.warehouse_id.show_stock_website_jz", "=", True),
                      ('product_id', '=', res['product_id'])]

            quants = self.env["stock.quant"].sudo().search(domain)

            stock_locations = {

            }

            if quants:
                for quant in quants:

                    if quant.location_id.warehouse_id.id in stock_locations:
                        stock_locations.update({
                            quant.location_id.warehouse_id.id: {
                                'warehouse': quant.location_id.warehouse_id.display_name,
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

            html = ''

            if res_locations:

                stock_total = 0

                html = ''
                for stock_wa in res_locations:
                    html += f'''<li class="list-group-item">{stock_wa['warehouse']} : {stock_wa['stock']}  </li>'''
                    stock_total += stock_wa['stock']


                html = f'''
                
                <div class="accordion" id="accordionExample">
                      <div class="accordion-item">
                          <h2 class="accordion-header" id="headingOne">
                               <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                   Stock Disponible: {stock_total}
                               </button>
                          </h2>
                          <div id="collapseOne" class="accordion-collapse collapse " aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                            <div class="accordion-body">
                                 {html}
                            </div>
                          </div>
                      </div>
                </div>

                '''




            res.update({
                'html_warehouses' : html
            })

        return res
