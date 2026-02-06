from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools.float_utils import float_repr, float_round
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _amount_detration(self):
        res = self._l10n_pe_edi_get_spot()
        if 'payment_percent' in res and 'spot_amount' in res and 'amount' in res:
            return res['amount']
        else:
            return 0

        # max_percent = max(self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
        # amount =round(self.currency_id.with_context(date=self.invoice_date, disable_rate_date_check=True)._convert((self.amount_total * max_percent)/100.0, self.env['res.currency'].search([('name', '=', 'PEN')])) + 0.01, 0)
        # return amount

    def _net_payable(self, amount_total):
        amount_detraction = self._amount_detration()
        if self.currency_id.name != 'PEN':
            return amount_total - (amount_total*(self._amount_percent()/100))
            # amount_detraction = self.company_id.currency_id._convert(amount_detraction, self.currency_id, self.company_id, self.invoice_date or datetime.today().strftime('%Y-%m-%d'))
        amount = amount_total - amount_detraction
        return amount

    def _detration_banck(self):
        bank=''
        if self.env.company.partner_id.bank_ids:
            for bank_obj in self.env.company.partner_id.bank_ids:
                if bank_obj.bank_bic =='BANCPEPL':
                    bank=bank_obj.acc_number
                    break
        return bank

    def _amount_percent(self):
        PaymentPercent = max(self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
        return PaymentPercent

    def _get_currency_detration_name(self):
        res = self.env['res.currency'].search([('name', '=', 'PEN')])
        return res

    def _free_operations(self):
        tax_free_ids = self.env['account.tax'].search([('l10n_pe_edi_tax_code', '=', '9996'), ('name', 'ilike', 'Free'),('company_id','=',self.company_id.id)])
        sum_amount = 0.0
        for line in self.invoice_line_ids:
            for tax in line.tax_ids:
                if tax.id in tax_free_ids.ids:
                    sum_amount += line.price_subtotal
        # amount = sum(l.price_subtotal for l in self.invoice_line_ids.filtered(lambda l: tax_free.id in l.tax_ids.ids))
        return sum_amount

    def _other_charges(self):
        amount = 0.00
        return amount

    def _amount_igv(self):
        amount = 0.0
        cadena = self.tax_totals
        if cadena.get('subtotals', False):
            name = cadena['subtotals'][0]['name']
            igv = cadena['groups_by_subtotal'][name][0]['tax_group_amount'] if cadena['groups_by_subtotal'][name][0]['tax_group_name'] != 'GRA' else 0.0
            if igv:
                amount = igv
        return amount
    
    def _get_amount_untaxed(self):
        free_amount = self._free_operations()
        amount = self.amount_untaxed - free_amount
        return amount
        

    def _payment_credit(self):
        if self.env['ir.module.module'].sudo().search([('name', '=', 'l10n_pe_credit_payments_pdf')]).state == 'installed':
            return True
        else:
            return False

    def _agent_retention(self):
        if self.env['ir.module.module'].sudo().search([('name', '=', 'l10n_pe_agent_retention_pdf')]).state == 'installed':
            return True
        else:
            return False

    # def _prepare_retention(self):
    #     return {}
