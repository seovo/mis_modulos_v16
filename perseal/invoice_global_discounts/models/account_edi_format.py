# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, _lt


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super(AccountEdiFormat, self)._l10n_pe_edi_get_edi_values(invoice)
        if invoice.invoice_line_ids.filtered(lambda x: x.price_subtotal < 0 and x.product_id.is_gobal_discount):
            amount_discount = sum(invoice.mapped('invoice_line_ids').filtered(lambda x: x.price_subtotal < 0 and x.product_id.is_gobal_discount).mapped('price_subtotal')) * -1
            values['multiplier'] = round(amount_discount / (invoice.amount_untaxed + amount_discount), 5)
            values['amount_discount'] = amount_discount
            values['amount_untaxed'] = invoice.amount_untaxed + amount_discount
            values['tax_amount'] = invoice.amount_tax_signed
            if invoice.move_type == 'out_refund':
                for l in values['invoice_line_vals_list']:
                    l['price_total_unit'] = l['price_total_unit'] * values['multiplier']
        return values
