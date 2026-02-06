# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_gobal_discount = fields.Boolean(string="Is Global Discount", default=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_gobal_discount = fields.Boolean(string="Is Global Discount", related="product_tmpl_id.is_gobal_discount")