# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    # def reconcile(self, lines_vals_list, to_check=False, allow_partial=False):
    #     super(AccountBankStatementLine, self).reconcile(lines_vals_list, to_check=to_check, allow_partial=allow_partial)
    #     self.move_id.action_lines_redistribute()
