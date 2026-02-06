# -*- coding: utf-8 -*-

from odoo import models, api


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super(AccountEdiFormat, self)._l10n_pe_edi_get_edi_values(invoice)
        values['retention'] = invoice._prepare_retention()
        return values
