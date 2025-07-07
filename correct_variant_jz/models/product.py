# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from itertools import chain
from odoo.http import request

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    


class ProductProduct(models.Model):
    _inherit = "product.product"

    def compute_combination_indices_all(self):
        products = self.env['product.product'].search([('combination_indices','=',False)],limit=1000)
        if products:
            products.compute_combination_indices()

    def compute_combination_indices(self):
        for product in self:
            product.combination_indices = product.product_template_attribute_value_ids._ids2str()