# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_edi_vals_to_export(self):
        res = super(AccountMove, self)._prepare_edi_vals_to_export()
        if self.invoice_line_ids.filtered(lambda line: not line.display_type and line.price_subtotal > 0):
            res = {
                'record': self,
                'balance_multiplicator': -1 if self.is_inbound() else 1,
                'invoice_line_vals_list': [],
            }
            for index, line in enumerate(self.invoice_line_ids.filtered(lambda line: not line.display_type and line.price_subtotal > 0), start=1):
                line_vals = line._prepare_edi_vals_to_export()
                line_vals['index'] = index
                res['invoice_line_vals_list'].append(line_vals)
            res.update({
                'total_price_subtotal_before_discount': sum(
                    x['price_subtotal_before_discount'] for x in res['invoice_line_vals_list']),
                'total_price_discount': sum(x['price_discount'] for x in res['invoice_line_vals_list']),
            })
        return res