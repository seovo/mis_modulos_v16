from odoo import models


class AccountEdiXmlUBLPE(models.AbstractModel):
    _inherit = 'account.edi.xml.ubl_pe'

    def _export_invoice_vals(self, invoice):
        vals = super()._export_invoice_vals(invoice)
        if invoice.partner_id.order_ref_in_invoice:
            if invoice.number_order_reference not in ['', False]:
                vals['vals']['order_reference'] = invoice.number_order_reference
            else:
                vals['vals']['order_reference'] = invoice.invoice_origin
        else:
            vals['vals']['order_reference'] = ''
            vals['vals']['sales_order_id'] = ''
        return vals
        
    
