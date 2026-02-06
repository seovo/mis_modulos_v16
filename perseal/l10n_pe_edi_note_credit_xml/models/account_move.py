# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_repr, float_round


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_pe_edi_get_spot(self):
        res = super(AccountMove, self)._l10n_pe_edi_get_spot()
        max_percent = max(self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
        max_amount = 400 if '027' in self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_code') else 700
        if not max_percent or self.amount_total_signed < max_amount or not self.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004'] or self.l10n_latam_document_type_id.code == '07':
            return {}
        return res