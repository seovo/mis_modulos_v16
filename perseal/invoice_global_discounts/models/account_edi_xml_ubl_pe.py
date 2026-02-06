from odoo import models


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _export_invoice_vals(self, invoice):
        # EXTENDS account.edi.xml.ubl_21
        vals = super()._export_invoice_vals(invoice)
        vals_lines = [item for item in vals['vals']['line_vals'] if item['line_quantity'] >= 0]
        vals['vals']['line_vals'] = vals_lines
        if invoice.invoice_line_ids.filtered(lambda x: x.price_subtotal < 0 and x.product_id.is_gobal_discount):
            amount_discount = sum(invoice.mapped('invoice_line_ids').filtered(lambda x: x.price_subtotal < 0 and x.product_id.is_gobal_discount).mapped('price_subtotal')) * -1
            vals['vals']['allowance_charge_vals'] = [{'charge_indicator': 'false',
                                                      'allowance_charge_reason_code': '02',
                                                      'multiplier_factor': round(amount_discount / (invoice.amount_untaxed + amount_discount), 5),
                                                      'amount': amount_discount,
                                                      'currency_dp': 2,
                                                      'base_amount': invoice.amount_untaxed + amount_discount,
                                                      'currency_name': invoice.currency_id.name}]
        return vals