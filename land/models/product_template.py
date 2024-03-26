# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models , api
from odoo.tools.translate import html_translate
from odoo.http import request

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'
    @api.onchange('attribute_id')
    def  change_attribute_id(self):
        for record in self:
            if record.attribute_id.type_land:
                idsx = []
                for value in record.attribute_id.value_ids:
                    idsx.append(value.id)
                #raise ValueError(idsx)
                record.value_ids = [(6,0,idsx)]

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    payment_land_dues = fields.Boolean(string="Pagados x Cuotas")
    dues_qty = fields.Integer(string="N° Cuotas")
    is_advanced_land = fields.Boolean(string="Adelanto Terreno")



    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if product_id:
            product = self.env['product.product'].browse(product_id)
            price = self.env['sale.order.line']._price_land(product,returnx=True,qty=add_qty)
            if price:
                combination_info.update({
                    'list_price': price,
                    'price': price

                })



        return combination_info
        raise ValueError(combination_info)

        if not self.env.context.get('website_sale_stock_get_quantity'):
            return combination_info

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            website = self.env['website'].get_current_website()
            free_qty = product.with_context(warehouse=website._get_warehouse_available()).free_qty
            has_stock_notification = product._has_stock_notification(self.env.user.partner_id) \
                                     or request \
                                     and product.id in request.session.get('product_with_stock_notification_enabled',
                                                                           set())
            stock_notification_email = request and request.session.get('stock_notification_email', '')
            combination_info.update({
                'free_qty': free_qty,
                'product_type': product.type,
                'product_template': self.id,
                'available_threshold': self.available_threshold,
                'cart_qty': product._get_cart_qty(website),
                'uom_name': product.uom_id.name,
                'allow_out_of_stock_order': self.allow_out_of_stock_order,
                'show_availability': self.show_availability,
                'out_of_stock_message': self.out_of_stock_message,
                'has_stock_notification': has_stock_notification,
                'stock_notification_email': stock_notification_email,
            })
        else:
            product_template = self.sudo()
            combination_info.update({
                'free_qty': 0,
                'product_type': product_template.type,
                'allow_out_of_stock_order': product_template.allow_out_of_stock_order,
                'available_threshold': product_template.available_threshold,
                'product_template': product_template.id,
                'cart_qty': 0,
            })

        return combination_info

    def _is_sold_out(self):
        return self.product_variant_id._is_sold_out()

    def _website_show_quick_add(self):
        return (self.allow_out_of_stock_order or not self._is_sold_out()) and super()._website_show_quick_add()
