from odoo import models


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _get_invoice_payment_terms_vals_list(self, invoice):
        spot = invoice._l10n_pe_edi_get_spot()
        if spot:
            spot_amount = spot['amount'] if invoice.currency_id == invoice.company_id.currency_id else spot['spot_amount']
        invoice_date_due_vals_list = []
        first_time = True
        for rec_line in invoice.line_ids.filtered(lambda l: l.account_type == 'asset_receivable').sorted('date_maturity'):
            amount = rec_line.amount_currency
            if spot and first_time:
                amount -= spot_amount
            first_time = False
            invoice_date_due_vals_list.append({
                'currency_name': rec_line.currency_id.name,
                'currency_dp': rec_line.currency_id.decimal_places,
                'amount': amount,
                'date_maturity': rec_line.date_maturity,
            })
        if not spot:
            total_after_spot = abs(invoice.amount_total)
        else:
            total_after_spot = abs(invoice.amount_total) - spot_amount
        payment_means_id = invoice._l10n_pe_edi_get_payment_means()
        vals = []
        if spot:
            vals.append({
                'id': spot['id'],
                'currency_name': 'PEN',
                'currency_dp': 2,
                'payment_means_id': spot['payment_means_id'],
                'payment_percent': spot['payment_percent'],
                'amount': spot['amount'],
            })
        if invoice.move_type not in ('out_refund', 'in_refund') or invoice.l10n_pe_edi_refund_reason == '13':
            if payment_means_id == 'Contado':
                vals.append({
                    'id': 'FormaPago',
                    'payment_means_id': payment_means_id,
                })
            else:
                vals.append({
                    'id': 'FormaPago',
                    'currency_name': invoice.currency_id.name,
                    'currency_dp': invoice.currency_id.decimal_places,
                    'payment_means_id': payment_means_id,
                    'amount': total_after_spot,
                })
                for i, due_vals in enumerate(invoice_date_due_vals_list):
                    vals.append({
                        'id': 'FormaPago',
                        'currency_name': due_vals['currency_name'],
                        'currency_dp': due_vals['currency_dp'],
                        'payment_means_id': 'Cuota' + '{0:03d}'.format(i + 1),
                        'amount': due_vals['amount'],
                        'payment_due_date': due_vals['date_maturity'],
                    })
        if vals:
            if vals[0].get('id', False) == 'Detraccion':
                return vals
            if invoice.retention_amount > 0 and invoice.l10n_pe_edi_operation_type == '0101' and invoice.partner_id.agent_retention:
                for item in vals:
                    if 'payment_means_id' in item and item['payment_means_id'] in ['Cuota001', 'Credito']:
                        item['amount'] -= invoice.retention_amount
        if invoice.invoice_cred and invoice.l10n_pe_edi_refund_reason == '13':
            amount_total = sum(line.amount_due for line in invoice.invoice_cred)
            vals_quotas = {}
            for l in invoice.invoice_cred:
                vals_quotas[l.number_due] = l.amount_due
            vals[0]['amount'] = amount_total
            for x in vals:
                if vals_quotas.get(x['payment_means_id'], False):
                    x['amount'] = vals_quotas[x['payment_means_id']] 
        return vals