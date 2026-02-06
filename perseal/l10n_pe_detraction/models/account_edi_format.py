# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, _lt


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super(AccountEdiFormat, self)._l10n_pe_edi_get_edi_values(invoice)
        invoice._l10n_pe_edi_get_detraction(values)
        return values