# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from itertools import chain
from odoo.http import request

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"
    new_price_comparation = fields.Float(
        'Precio Comparación', store=True,
        digits='Product Price')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
            self, combination=False, product_id=False, add_qty=1.0,
            parent_combination=False, only_template=False,
    ):
        res = super()._get_combination_info(combination, product_id, add_qty,
            parent_combination, only_template)

        if product_id:
            product = self.env['product.product'].browse(product_id)
            res.update({
                'compare_list_price': product.new_price_comparation
            })


        return res