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





    def get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                             parent_combination=False, only_template=False):
        res = super().get_combination_info(combination, product_id, add_qty, pricelist,
                             parent_combination, only_template)
        raise ValueError(res)
        return res