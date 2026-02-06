# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_advance_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('l10n_pe_down_payments_edi.down_payment_product_id')
        if product_id:
            return self.env['product.product'].browse(int(product_id)) or False
        else:
            return False

    advance_product_id = fields.Many2one('product.product', string='Advance Product', default=_get_advance_product_id)
    l10n_pe_edi_operation_type = fields.Selection(selection_add=[('04', "[04] Venta interna - Anticipos")])
    invoice_balance_id = fields.Many2one('account.move', string='Balance Invoice', copy=False,)
    invoice_advance_ids = fields.One2many('account.move', 'invoice_balance_id', copy=False,
                                          string='Advance Invoice',)
                                          # domain="[('invoice_line_ids.product_id', '=', advance_product_id),('partner_id', '=', partner_id),('invoice_balance_id', '=', False),('invoice_advance_ids','=',False),('state', '=', 'posted'),('move_type', '=', 'out_invoice'),('edi_state', '=', 'to_send')]")

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

    @api.onchange('invoice_advance_ids')
    def _onchange_advance_product_id(self):
        if self.invoice_advance_ids:
            product_id = int(self.env['ir.config_parameter'].sudo().get_param('l10n_pe_down_payments_edi.down_payment_product_id'))
            for advance in self.invoice_advance_ids:
                tax_ids = advance.invoice_line_ids.mapped('tax_ids')
                account_id = advance.invoice_line_ids.mapped('account_id')
                if not self.invoice_line_ids.filtered(lambda x: 'Pagos anticipados' in x.name):
                    self.env['account.move.line'].create({
                        'move_id': self._origin.id,
                        'display_type': 'line_section',
                        'name': 'Pagos anticipados',
                    })
                if not self.invoice_line_ids.filtered(lambda x: advance.name in x.name):
                    line_id = self.env['account.move.line'].create({
                        'move_id': self._origin.id,
                        'product_id': product_id,
                        'quantity': -1,
                        'price_unit': advance.amount_untaxed,
                        'name': 'Anticipo ' + advance.name,
                        'tax_ids': [(6, 0, tax_ids.ids)],
                        'account_id': account_id.id,
                        'display_type': 'product',
                        'currency_id': advance.currency_id.id,
                    })
                    # line_id._compute_totals()
            # self._move_autocomplete_invoice_lines_values()