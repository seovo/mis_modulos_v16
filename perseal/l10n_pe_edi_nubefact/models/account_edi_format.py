# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'
    
    def _l10n_pe_edi_sign_invoices_nubefact(self, invoice, edi_filename, edi_str):
        self.ensure_one()
        vals = self.env['account.edi.xml.ubl_pe']._export_invoice_vals(invoice)
        
        self.env['nubefact.api'].send_nubefact(invoice=invoice, vals=vals)
