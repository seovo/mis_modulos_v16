# -*- coding: utf-8 -*-

import math

from odoo import api, fields, models
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            if line.move_id.is_sale_document(include_receipts=True):
                document_type = 'sale'
            elif line.move_id.is_purchase_document(include_receipts=True):
                document_type = 'purchase'
            else:
                document_type = 'other'
            date_rate = line.move_id.date
            if line.move_id.move_type in ['in_invoice', 'in_refund']:
                date_rate = line.move_id.invoice_date or line.move_id.date
            line.price_unit = line.product_id._get_tax_included_unit_price(
                line.move_id.company_id,
                line.move_id.currency_id,
                date_rate,
                document_type,
                fiscal_position=line.move_id.fiscal_position_id,
                product_uom=line.product_uom_id,
            )