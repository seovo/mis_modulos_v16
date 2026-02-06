# -*- coding: utf-8 -*-

from odoo import models, api, _, _lt


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_get_edi_values(self, invoice):
        values = super()._l10n_pe_edi_get_edi_values(invoice)
        product_id = int(self.env['ir.config_parameter'].sudo().get_param('l10n_pe_down_payments_edi.down_payment_product_id'))
        if invoice.invoice_line_ids.filtered(lambda l: l.product_id.id == product_id and l.quantity < 0) and not invoice.invoice_advance_ids and invoice.move_type == 'out_invoice':
            sale_order_origin = invoice.invoice_line_ids.sale_line_ids.order_id
            invoices_sale_order_origin = sale_order_origin.order_line.invoice_lines.move_id.filtered(lambda m: m.move_type in ('out_invoice') and not m.invoice_balance_id and m.state == 'posted' and m.edi_state == 'sent') - invoice
            invoices_advance = invoices_sale_order_origin.invoice_line_ids.filtered(lambda l: l.product_id.id == product_id).mapped('move_id')
            invoice.update({'invoice_advance_ids': [(6, False, invoices_advance.ids)]})
        if invoice.invoice_advance_ids and invoice.edi_state != 'sent':
            values['amount_tax'] = invoice.amount_tax
            values['down_payment'] = {'prepaid': []}
            advance_amount = 0
            advance_amount_igv = 0
            amount_tax = 0
            for line in invoice.invoice_advance_ids:
                prepaid = {'partner_id': line.partner_id,
                           'invoice': line,
                           'document_type': '02' if line.l10n_latam_document_type_id.code == '01' else line.l10n_latam_document_type_id.code,
                           'amount': round(line.amount_untaxed, 2),
                           'amount_igv': round(line.amount_total, 2),
                           'amount_tax': round(invoice.amount_tax, 2)}
                advance_amount += line.amount_untaxed
                advance_amount_igv += line.amount_total
                amount_tax += line.amount_tax
                values['down_payment']['prepaid'].append(prepaid)
            values['down_payment'].update({'TaxAmount': round(advance_amount, 2),
                                           'amount_untaxed': round((advance_amount + invoice.amount_untaxed), 2),
                                           'amount_total': round((advance_amount_igv + invoice.amount_total), 2),
                                           'TaxableAmount': round(advance_amount_igv, 2),
                                           'AmountTax': round(amount_tax, 2),
                                           'currency': invoice.currency_id.name,
                                           'multiplier': round(advance_amount/(advance_amount + invoice.amount_untaxed), 5)})
        return values
