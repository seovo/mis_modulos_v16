# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models , api
from odoo.tools.translate import html_translate
from odoo.http import request


class ProductProduct(models.Model):
    _inherit = 'product.product'
    manzana = fields.Char(store=True,compute='get_label_values_attribute_values')
    lote = fields.Char(store=True,compute='get_label_values_attribute_values')

    @api.depends('product_template_attribute_value_ids')
    def get_label_values_attribute_values(self):
        for record in self:
            manzana = ''
            lote = ''
            for lvav in record.product_template_attribute_value_ids:
                if lvav.attribute_id.type_land == 'mz':
                    manzana = lvav.product_attribute_value_id.name
                if lvav.attribute_id.type_land == 'lot':
                    lote = lvav.product_attribute_value_id.name
            record.manzana = manzana
            record.lote = lote