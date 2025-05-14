from odoo import api, Command, fields, models, _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    product_repair_id = fields.Many2one('product.product',string="Producto a reparar")
    cat_bycle_id = fields.Many2one('category.bycle',string='Categoria')
    under_warranty_bycle = fields.Selection([('taller','Taller'),('purchase','Compra')],string='Bajo Garantia')


class CategoryBycle(models.Model):
    _name = 'category.bycle'
    _description = 'category.bycle'
    name = fields.Char()
