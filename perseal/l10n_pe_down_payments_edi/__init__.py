# -*- coding: utf-8 -*-

from . import models

# from odoo import api, SUPERUSER_ID
#
# def function_down_payment_product_id(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     if env['ir.module.module'].search([('name', '=', 'sale')]).state == 'installed':
#         for line in env['res.company'].search([]):
#             if env['res.config.settings'].search([('company_id', '=', line.id)]):
#                 product = env['res.config.settings'].search([('company_id', '=', line.id)])[0].deposit_default_product_id
#                 line.down_payment_product_id = product
