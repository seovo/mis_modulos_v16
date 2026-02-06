# -*- coding: utf-8 -*-

import math

from odoo import api, fields, models
from datetime import datetime


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        if self.move_id.move_type in ['in_invoice', 'in_refund']:
            date = self.move_id.invoice_date
        return super(AccountMoveLine, self)._get_fields_onchange_subtotal(price_subtotal, move_type, currency, company, date)

    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            company = line.move_id.company_id
            date = line.move_id.date if line.move_id.move_type not in ['in_invoice', 'in_refund'] else line.move_id.invoice_date
            balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, date or fields.Date.context_today(line))
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())