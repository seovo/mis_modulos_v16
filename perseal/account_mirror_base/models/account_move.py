# -*- coding: utf-8 -*-
from contextlib import ExitStack, contextmanager
from odoo.tools import float_compare
from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model_create_multi
    def create(self, vals_list):
        move = super(AccountMove, self).create(vals_list)
        for ml in move:
            if ml.move_type not in ['out_refund', 'in_refund']:
                self.create_line_of_distribution(ml.line_ids, ml)
        return move

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for line in self:
            if line._context.get('distribution', True) and line.move_type not in ['out_refund', 'in_refund'] and line.state not in ['posted'] and 'invoice_line_ids' in vals or 'line_ids' in vals:
                line.line_ids.filtered(lambda r: r.is_distribution).unlink()
                line.create_line_of_distribution(line.line_ids, line)
        return res

    def get_keys_json_analytic_distribution(self, json_data):
        keys_ids = [int(key) for key in json_data.keys()]
        return self.env['account.analytic.account'].browse(keys_ids).filtered(lambda l: l.account_credit_id and l.account_debit_id)

    def create_line_of_distribution(self, line_ids, move_id):
        for line in line_ids.filtered(lambda r: r.account_id.account_type in ['expense', 'expense_depreciation']):
            tag_distribution = self.get_keys_json_analytic_distribution(line.analytic_distribution if line.analytic_distribution else {})
            lines_vals = []
            for x in tag_distribution:
                amount = line.credit
                credit = line.credit
                debit = line.debit
                if credit == 0:
                    amount = debit
                amount = amount * (line.analytic_distribution[str(x.id)]/100)
                lines_vals.append({
                    'account_id': x.account_credit_id.id if line.debit > 0 else x.account_debit_id.id,
                    'name': move_id.ref or _('Distribution Lines - {}'.format(x.name)),
                    'balance': -amount,
                    'amount_currency': -amount,
                    'move_id': move_id.id,
                    'is_distribution': True,
                    'display_type': 'cogs',
                })
                lines_vals.append({
                    'account_id': x.account_debit_id.id if line.debit > 0 else x.account_credit_id.id,
                    'name': move_id.ref or _('Distribution Lines - {}'.format(x.name)),
                    'balance': amount,
                    'amount_currency': amount,
                    'move_id': move_id.id,
                    'is_distribution': True,
                    'display_type': 'cogs',
                })
            if line.account_id.have_target_account:
                amount = credit = line.credit
                debit = line.debit
                if credit == 0: amount = debit
                lines_vals.append({
                    'account_id': line.account_id.target_account_credit.id if line.debit > 0 else line.account_id.target_account_debit.id,
                    'name': move_id.ref or _('Distribution Lines - {}'.format(line.name)),
                    'balance': -amount,
                    'amount_currency': -amount,
                    'move_id': move_id.id,
                    'is_distribution': True,
                    'display_type': 'cogs',
                })
                lines_vals.append({
                    'account_id': line.account_id.target_account_debit.id if line.debit > 0 else line.account_id.target_account_credit.id,
                    'name': move_id.ref or _('Distribution Lines - {}'.format(line.name)),
                    'balance': amount,
                    'amount_currency': amount,
                    'move_id': move_id.id,
                    'is_distribution': True,
                    'display_type': 'cogs',
                })
            else:
                if line.id not in move_id.invoice_line_ids.ids:
                    line.write({'name': move_id.ref})
            self.env['account.move.line'].create(lines_vals)
            
            
    @api.depends('line_ids.balance')
    def _compute_depreciation_value(self):
        for move in self:
            asset = move.asset_id or move.reversed_entry_id.asset_id  # reversed moves are created before being assigned to the asset
            if asset:
                account_internal_group = 'expense'
                asset_depreciation = sum(
                    move.line_ids.filtered(lambda l: not l.is_distribution and l.account_id.internal_group == account_internal_group or l.account_id == asset.account_depreciation_expense_id).mapped('balance')
                )

                if any(
                    line.account_id == asset.account_asset_id
                    and float_compare(-line.balance, asset.original_value, precision_rounding=asset.currency_id.rounding) == 0
                    for line in move.line_ids
                ) and len(move.line_ids) > 2:
                    asset_depreciation = (
                        asset.original_value
                        - asset.salvage_value
                        - (
                            move.line_ids[1].debit if asset.original_value > 0 else move.line_ids[1].credit
                        ) * (-1 if asset.original_value < 0 else 1)
                    )
            else:
                asset_depreciation = 0
            move.depreciation_value = asset_depreciation


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    is_distribution = fields.Boolean(default=False)
