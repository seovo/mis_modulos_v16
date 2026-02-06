# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from num2words import num2words


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.model
    def _l10n_pe_edi_amount_to_text(self, amount, currency):
        """Transform a float amount to text words on peruvian format: AMOUNT IN TEXT 11/100
        :returns: Amount transformed to words peruvian format for invoices
        :rtype: str
        """
        self.ensure_one()
        amount_i, amount_d = divmod(float(amount), 1)
        amount_d = int(round(amount_d * 100, 2))
        words = num2words(amount_i, lang='es')
        result = '%(words)s Y %(amount_d)02d/100 %(currency_name)s' % {
            'words': words,
            'amount_d': amount_d,
            'currency_name': currency.currency_unit_label,
        }
        return result.upper()

    def get_currency_name(self):
        if self.currency_id.name == 'PEN':
            return 'Soles'
        else:
            return 'Dólares'

    def get_info_tax_totals(self,tax_totals):
        data = {}
        data['formatted_amount_total'] = tax_totals['formatted_amount_total']
        data['formatted_amount_untaxed'] = tax_totals['formatted_amount_untaxed']
        formatted_tax_group_amount = 0
        for group in tax_totals['groups_by_subtotal']['Subtotal']:
            if group['tax_group_name'] == 'IGV':
                formatted_tax_group_amount = group['formatted_tax_group_amount']
        data['formatted_tax_group_amount'] = formatted_tax_group_amount

        amount_total = round((1/self.currency_rate) * self.amount_total,2)
        data['amount_total'] = amount_total
        data['amount_total_str'] = 'S/ ' + str(amount_total)
        data['rate'] = 'T/C = ' + str(round(1/self.currency_rate,2))
        return data
