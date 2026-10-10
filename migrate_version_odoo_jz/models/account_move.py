from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'



    def set_compute_amount(self):
        self._compute_amount_jz()
        self._compute_amount()

    def _compute_amount_jz(self):
        self.line_ids.fetch([
            'debit',
            'balance',
            'amount_currency',
            'amount_residual',
            'amount_residual_currency',
            'display_type',
            'tax_repartition_line_id'
        ])
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_reconciled, total_reconciled_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type in ('tax', 'non_deductible_tax') or (
                            line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in (
                    'product', 'rounding', 'non_deductible_product', 'non_deductible_product_total'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Reconciled amount.
                        total_reconciled += line.balance - line.amount_residual
                        total_reconciled_currency += line.amount_currency - line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            raise ValueError(total_currency)

            sign = move.direction_sign
            tax_totals = move.tax_totals or {}
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = tax_totals.get('total_amount_currency', 0.0) + sign * total_reconciled_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_untaxed_in_currency_signed = -total_untaxed_currency
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = -sign * tax_totals.get('total_amount', 0.0) - total_reconciled
            move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(
                        sign * move.amount_total)