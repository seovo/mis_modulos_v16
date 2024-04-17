from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

class AccountMove(models.Model):
    _inherit = 'account.move'
    narration = fields.Text()