# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super()._l10n_pe_edi_get_edi_values(invoice)
        def format_float_fixed(amount, precision=2):
            ''' Helper to format monetary amount as a string with 2 decimal places. '''
            if amount is None or amount is False:
                return None
            return '%.*f' % (precision, abs(amount))

        values.update({'format_float': format_float_fixed})
        return values

