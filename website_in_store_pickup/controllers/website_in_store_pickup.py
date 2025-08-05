
###############################################################################
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.delivery import WebsiteSaleDelivery


class WebsiteInStorePickup(WebsiteSaleDelivery):
    """ Inherited  Controller to check the carrier and update in corresponding
     sale order"""
    @http.route(['/shop/check_carrier'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def check_carrier(self, **post):
        """To check the carrier details and returns the relevant details
        whether the delivery method is store pick or not and returns the
        available stores"""
        carrier_id = int(post.get('carrier_id'))
        store = request.env['sucursales.toys'].sudo().search([])
        carrier = request.env['delivery.carrier'].sudo().browse(carrier_id)
        sale_order_id = http.request.session.get('sale_order_id')

        dx = {
            'is_store_pick': carrier.is_store_pick,
            'store_ids': carrier.store_ids.read(),
            'store_id': store.read(),
            'sale_order_id': sale_order_id

        }

        if sale_order_id:
            sale_order = http.request.env['sale.order'].sudo().browse(
                sale_order_id)
            dx.update({
                'sale_order_id':  sale_order.id ,
                'warehouse_id':sale_order.sucursal_toy_id.id
            })
            #if not carrier.is_store_pick:
            #    sale_order.write({
            #        'partner_invoice_id': sale_order.partner_id.id,
            #        'partner_shipping_id': sale_order.partner_id.id,
            #    })
        return dx

    @http.route(['/shop/update_address'], type='json', auth='public',
                methods=['POST'], website=True, csrf=False)
    def update_addressx(self, **post):
        sale_order_id = http.request.session.get('sale_order_id')
        sale_order = http.request.env['sale.order'].sudo().browse(
            sale_order_id)
        if 'store_id' not in post:
            sale_order.sucursal_toy_id = None
            return

        if not post['store_id']:
            sale_order.sucursal_toy_id = None
            return

        try:
            if int(post['store_id']) == 0:
                sale_order.sucursal_toy_id = None
                return
        except:
            sale_order.sucursal_toy_id = None

            return


        """To update the address of store address to sale order on choosing
        the store for pickup"""
        store_address = request.env['sucursales.toys'].sudo().browse(
            int(post['store_id']))
        if post['store_id']:

            if sale_order:

                sale_order.sucursal_toy_id = store_address.id
                for line in sale_order.order_line :
                    if line.is_delivery:
                        line.name = f'''Recoger en {store_address.name}'''



                #sale_order.write({
                #    'partner_invoice_id': store_address.partner_id.id,
                #    'partner_shipping_id': store_address.partner_id.id
                #})
                return {
                    #'store_id': store_address.partner_id.read()
                    'store_id': store_address.read()
                        }
        return {
            #'store_id': store_address.partner_id.read()
            'store_id': store_address.read()

                }
