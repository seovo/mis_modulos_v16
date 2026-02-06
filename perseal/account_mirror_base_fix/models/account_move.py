# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_mirror_fix(self):
        self.write({'state': 'draft', 'is_move_sent': False})
        # account_expense = self.env['account.account.type'].search([('name', '=', 'Expenses')], limit=1)
        account_expense = self.env.ref('account.data_account_type_expenses')
        for ml in self:
            if ml.move_type not in ['out_refund', 'in_refund']:
                ml.line_ids.filtered(lambda r: r.is_distribution).unlink()
                for line in ml.line_ids.filtered(lambda r: r.account_id.user_type_id.id == account_expense.id):
                    tag_distribution = line.analytic_tag_ids.filtered(lambda l: l.active_analytic_distribution == True)
                    lines_vals = []
                    if len(tag_distribution) > 0 or line.account_id.have_target_account:
                        for x in tag_distribution:
                            amount = credit = line.credit
                            debit = line.debit
                            if credit == 0: amount = debit
                            for distribution in x.mapped('analytic_distribution_ids'):
                                lines_vals.append([0, 0, {
                                    'account_id': distribution.account_debit_id.id,
                                    'name': ml.ref or _('Distribution Lines - {}'.format(distribution.tag_id.name)),
                                    'credit': 0.0,
                                    'debit': (amount * distribution.percentage) / 100,
                                    'is_distribution': True,
                                    'exclude_from_invoice_tab': True,
                                }])
                                lines_vals.append([0, 0, {
                                    'account_id': distribution.account_credit_id.id,
                                    'name': ml.ref or _('Distribution Lines - {}'.format(distribution.tag_id.name)),
                                    'credit': (amount * distribution.percentage) / 100,
                                    'debit': 0.0,
                                    'is_distribution': True,
                                    'exclude_from_invoice_tab': True,
                                }])
                            # ml.with_context({'distribution': False}).line_ids = lines_vals
                        if line.account_id.have_target_account:
                            amount = credit = line.credit
                            debit = line.debit
                            if credit == 0: amount = debit
                            lines_vals.append([0, 0, {
                                'account_id': line.account_id.target_account_debit.id,
                                'name': ml.ref or _('Distribution Lines - {}'.format(line.name)),
                                'credit': 0.0,
                                'debit': amount,
                                'is_distribution': True,
                                'exclude_from_invoice_tab': True,
                            }])
                            lines_vals.append([0, 0, {
                                'account_id': line.account_id.target_account_credit.id,
                                'name': ml.ref or _('Distribution Lines - {}'.format(line.name)),
                                'credit': amount,
                                'debit': 0.0,
                                'is_distribution': True,
                                'exclude_from_invoice_tab': True,
                            }])
                        ml.with_context({'distribution': False}).line_ids = lines_vals

                    else:
                        if line.id not in ml.invoice_line_ids.ids:
                            line.write({'name': ml.ref})
        self.write({'state': 'posted', 'is_move_sent': True})