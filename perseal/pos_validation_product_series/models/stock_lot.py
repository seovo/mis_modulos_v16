# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class StockLot(models.Model):
    _inherit = 'stock.lot'


    def get_serial_number_available(self, product_name=''):
        product_template_id = self.env['product.template'].search([('name', '=', product_name)])
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id.id )])
        serial_number = [l.name for l in self.search([('product_id', '=',product_id.id)])]
        return serial_number