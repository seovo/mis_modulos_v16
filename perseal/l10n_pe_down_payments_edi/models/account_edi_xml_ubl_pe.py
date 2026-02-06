from odoo import models


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _export_invoice_vals(self, invoice):

        vals = super()._export_invoice_vals(invoice)
        vals.update({
            'AdditionalDocumentReference_template': 'l10n_pe_down_payments_edi.ubl_20_AdditionalDocumentReference',
            'PrepaidPayment_template': 'l10n_pe_down_payments_edi.ubl_20_PrepaidPayment',
            'InvoiceType_template': 'l10n_pe_down_payments_edi.ubl_21_InvoiceType_pe',
        })
        product_id = int(self.env['ir.config_parameter'].sudo().get_param('l10n_pe_down_payments_edi.down_payment_product_id'))
        if invoice.invoice_line_ids.filtered(
                lambda l: l.product_id.id == product_id and l.quantity < 0) and not invoice.invoice_advance_ids and invoice.move_type == 'out_invoice':
            sale_order_origin = invoice.invoice_line_ids.sale_line_ids.order_id
            invoices_sale_order_origin = sale_order_origin.order_line.invoice_lines.move_id.filtered(
                lambda m: m.move_type in (
                    'out_invoice') and not m.invoice_balance_id and m.state == 'posted' and m.edi_state == 'sent') - invoice
            invoices_advance = invoices_sale_order_origin.invoice_line_ids.filtered(
                lambda l: l.product_id.id == product_id).mapped('move_id')
            invoice.update({'invoice_advance_ids': [(6, False, invoices_advance.ids)]})
        if invoice.invoice_advance_ids and invoice.edi_state != 'sent':
            vals['amount_tax'] = invoice.amount_tax
            vals['down_payment'] = {}
            vals['vals']['prepaid'] = []
            advance_amount = 0
            advance_amount_igv = 0
            amount_tax = 0
            for line in invoice.invoice_advance_ids:
                prepaid = {'partner_id': line.partner_id,
                           'invoice': line,
                           'document_type': '02' if line.l10n_latam_document_type_id.code == '01' else line.l10n_latam_document_type_id.code,
                           'amount': round(line.amount_untaxed, 2),
                           'amount_igv': round(line.amount_total, 2),
                           'amount_tax': round(invoice.amount_tax, 2),
                           'currency_dp': 2,}
                advance_amount += line.amount_untaxed
                advance_amount_igv += line.amount_total
                amount_tax += line.amount_tax
                vals['vals']['prepaid'].append(prepaid)
                vals['down_payment'].update({'TaxAmount': round(advance_amount, 2),
                                             'amount_untaxed': round((advance_amount + invoice.amount_untaxed), 2),
                                             'amount_total': round((advance_amount_igv + invoice.amount_total), 2),
                                             'TaxableAmount': round(advance_amount_igv, 2),
                                             'AmountTax': round(amount_tax, 2),
                                             'currency': invoice.currency_id.name,
                                             'multiplier': round(advance_amount / (advance_amount + invoice.amount_untaxed), 5)})
            vals['vals']['monetary_total_vals'].update({'prepaid_amount': round(advance_amount_igv, 2),
                                                        'line_extension_amount': round((advance_amount + invoice.amount_untaxed), 2),
                                                        'tax_inclusive_amount': round((advance_amount_igv + invoice.amount_total), 2)})
            vals['vals']['allowance_charge_vals'] = [{'charge_indicator': 'false',
                                                      'allowance_charge_reason_code': '04',
                                                      'multiplier_factor': round(advance_amount / (advance_amount + invoice.amount_untaxed), 5),
                                                      'amount': round(advance_amount, 2),
                                                      'currency_dp': 2,
                                                      'base_amount': round((advance_amount + invoice.amount_untaxed), 2),
                                                      'currency_name': invoice.currency_id.name}]
            vals_lines = [item for item in vals['vals']['line_vals'] if item['line_quantity'] >= 0]
            vals['vals']['line_vals'] = vals_lines
        return vals