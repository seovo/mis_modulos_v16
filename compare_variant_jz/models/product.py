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