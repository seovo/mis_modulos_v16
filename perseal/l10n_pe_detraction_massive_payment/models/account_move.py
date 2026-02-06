# -*- coding: utf-8 -*-


from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_post(self):
        res = super().action_post()
        if self.detraction_show:
            amount_detraction = self.detraction_amount
            self.create_line_account_move(amount_detraction)
        return res

    def create_line_account_move(self, amount_detraction):
        lines_vals = []
        line_id = self._get_detraction_account_id()
        lines_vals.append({
            'account_id': self.company_id.detraction_account_id.id if self.move_type == 'in_invoice' else line_id.account_id.id,
            'name': 'Detracción',
            'balance': -amount_detraction,
            'amount_currency': -amount_detraction,
            'move_id': self.id,
            'detraction': True,
            'reconciled': True,
            'amount_residual':0.0,
            'display_type': 'cogs' if self.move_type == 'in_invoice' else 'cogs',
        })
        lines_vals.append({
            'account_id': line_id.account_id.id if self.move_type == 'in_invoice' else self.company_id.detraction_account_id.id,
            'name': 'Detracción',
            'balance': amount_detraction,
            'amount_currency': amount_detraction,
            'move_id': self.id,
            'detraction': True,
            'reconciled': True,
            'amount_residual': 0.0,
            'display_type': 'cogs' if self.move_type == 'in_invoice' else 'cogs',
        })
        self.env['account.move.line'].create(lines_vals)

    def _get_detraction_account_id(self):
        if self.detraction_show:
            if self.move_type == 'in_invoice':
                line_id = self.line_ids.filtered(lambda r: r.credit == self.amount_total)
                return line_id
            elif self.move_type == 'out_invoice':
                line_id = self.line_ids.filtered(lambda r: r.debit == self.amount_total)
                return line_id
        return False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    detraction = fields.Boolean(string='Detraccion')

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            if not line.detraction:
                if line.move_id.is_sale_document(include_receipts=True):
                    if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                        raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
                if line.move_id.is_purchase_document(include_receipts=True):
                    if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                        raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))