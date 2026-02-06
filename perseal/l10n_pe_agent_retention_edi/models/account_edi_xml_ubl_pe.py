from odoo import models


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _export_invoice_vals(self, invoice):
        # EXTENDS account.edi.xml.ubl_21
        vals = super()._export_invoice_vals(invoice)
        values = invoice._prepare_retention()
        if len(values) > 0:
            vals['vals']['allowance_charge_vals'] = [{'charge_indicator': 'false',
                                                      'allowance_charge_reason_code': values['AllowanceChargeReasonCode'],
                                                      'multiplier_factor': values['MultiplierFactorNumeric'],
                                                      'amount': values['Amount'],
                                                      'currency_dp': 2,
                                                      'base_amount': values['BaseAmount'],
                                                      'currency_name': invoice.currency_id.name}]
        return vals