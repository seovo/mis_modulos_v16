# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    # def _prepare_edi_vals_to_export(self):
    #     res = super()._prepare_edi_vals_to_export()
    #     if self.l10n_pe_edi_affectation_reason == '37':
    #         res['price_subtotal_unit']= 0.0
    #     return res
        
        

        