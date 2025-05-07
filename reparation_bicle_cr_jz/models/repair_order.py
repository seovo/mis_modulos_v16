from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class RepairOrder(models.Model):
    _inherit = 'repair.order'
    order_line = fields.One2many('line.repair.order','repair_id')



class LineRepairOrder(models.Model):
    _name = 'line.repair.order'
    _description = 'line.repair.order'
    name = fields.Text(string='Descriptión',required=True)
    code = fields.Char(string='Codigo')
    price = fields.Float(string='Precio')
    user_id = fields.Many2one('res.users')
    product_ids = fields.Many2many('product.product')
    repair_id = fields.Many2one('repair.order')