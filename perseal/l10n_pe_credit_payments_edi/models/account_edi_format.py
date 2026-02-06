# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super()._l10n_pe_edi_get_edi_values(invoice)
        values['amount_credit'] =invoice._prepare_amount_credit()
        return values
