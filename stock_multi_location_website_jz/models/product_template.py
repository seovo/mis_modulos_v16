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
            product_idx = res['product_id']
        else:
            product_idx = self.product_variant_ids[0].id

        product = self.env['product.product'].search([('id','=',product_idx)])

        if product_id:
            domain = [("location_id.usage", "in", ["internal", "transit"]),
                      ("location_id.warehouse_id.show_stock_website_jz", "=", True),
                      ('product_id', '=', product_idx)]

            quants = self.env["stock.quant"].sudo().search(domain)

            stock_locations = {

            }

            if quants:
                for quant in quants:

                    stock = quant.quantity

                    typex  = quant.location_id.warehouse_id.type_show_website_jz

                    dictx = dict(location=quant.location_id.id, warehouse_id=quant.location_id.warehouse_id.id)


                    if typex == 'forecast':
                        stock = product.with_context(dictx).virtual_available

                    if typex == 'hand':
                        stock = product.with_context(dictx).qty_available


                    if quant.location_id.warehouse_id.id in stock_locations:


                        stock_new = stock_locations[quant.location_id.warehouse_id.id]['stock'] + stock

                        stock_locations.update({
                            quant.location_id.warehouse_id.id: {
                                'warehouse': quant.location_id.warehouse_id.display_name,
                                'stock': stock_new
                            }
                        })
                    else:
                        stock_locations.update({
                            quant.location_id.warehouse_id.id: {

                                'warehouse': quant.location_id.warehouse_id.display_name,
                                'stock': stock
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
                
                <div class="accordion m-2" id="accordionExample">
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
