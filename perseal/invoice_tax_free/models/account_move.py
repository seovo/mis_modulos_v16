# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api, _, Command


class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    def action_post(self):
        res = super().action_post()
        if all(tax.l10n_pe_edi_affectation_reason == '37' for line in self.invoice_line_ids for tax in line.tax_ids):
            self.l10n_pe_edi_legend = '1002'
        else:
            self.l10n_pe_edi_legend = ''
        return res