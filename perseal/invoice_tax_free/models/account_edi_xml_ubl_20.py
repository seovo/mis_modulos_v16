from odoo import models
from odoo.addons.l10n_pe_edi.models.account_edi_xml_ubl_pe import FREE_AFFECTATION_REASONS

FREE_AFFECTATION_REASONS += ['37']

class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'
    
    
    def _export_invoice_vals(self, invoice):
        res = super()._export_invoice_vals(invoice)
        # Ajustar solo las líneas gratuitas
        for tax_line in res['vals'].get('tax_total_vals', []):
            filtered_subs = []
            sum_amount_taxable = 0
            for tax_sub in tax_line.get('tax_subtotal_vals', []):
                scheme_id = tax_sub.get('tax_category_vals', {}).get('tax_scheme_vals',{}).get('id')
                if scheme_id in ['9996']:
                    tax_sub['tax_amount'] = 0.0
                if scheme_id != False:
                    filtered_subs.append(tax_sub)
                    sum_tax_amount = tax_sub['tax_amount']
                if scheme_id not in ['9996', False]:
                    sum_amount_taxable += tax_sub['taxable_amount']
            tax_line['tax_subtotal_vals'] = filtered_subs
            tax_line['tax_amount'] = sum_tax_amount
        res['vals']['monetary_total_vals']['line_extension_amount'] = sum_amount_taxable or 0.0
        # res['vals']['monetary_total_vals']['tax_inclusive_amount'] = invoice.amount_total

        return res
        
    def _get_invoice_line_vals(self, line, taxes_vals, idx=None):
        vals = super()._get_invoice_line_vals(line, taxes_vals, idx)
        if any(x.l10n_pe_edi_affectation_reason in ['37', '36'] for x in line.tax_ids):
            vals['free_of_charge_indicator'] = 'true'
            vals['price_subtotal'] = 0.0
            # vals['line_extension_amount'] = 0.0
            vals['price_subtotal_without_discount'] = 0.0
        return vals
    
    
    def _get_invoice_line_tax_totals_vals_list(self, line, taxes_vals):
        res = super()._get_invoice_line_tax_totals_vals_list(line, taxes_vals)
        if line.l10n_pe_edi_affectation_reason in ['37', '36']:
            for tax_line in res:
                filtered_subs = []
                for tax_sub in tax_line.get('tax_subtotal_vals', []):
                    if tax_sub['tax_category_vals']['tax_exemption_reason_code'] == '37':
                        tax_sub['tax_amount'] = 0.0
                        tax_sub['tax_category_vals']['percent'] = 0.0
                    if tax_sub['tax_category_vals']['tax_scheme_vals']['id'] != False:
                        filtered_subs.append(tax_sub)
                tax_line['tax_subtotal_vals'] = filtered_subs
        return res