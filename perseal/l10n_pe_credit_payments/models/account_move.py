# -*- coding: utf-8 -*-

import math

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    l10n_pe_edi_refund_reason = fields.Selection(selection_add=[('13', 'Corrección del monto neto pendiente de pago'
                                                                       ' y/o la(s) fechas(s) de vencimiento del pago'
                                                                       ' único o de las cuotas y/o los montos'
                                                                       ' correspondientes a cada cuota de ser el caso')])

    invoice_cred = fields.One2many('account.invoice.credit', 'account_move_credit', string='Pagos Por Cuota ')
    count_invoice_cred = fields.Boolean(string='Pagos Por Cuota', compute='compute_count_invoice_cred')

    def get_restante(self, invoice):
        detration = 0.00
        if invoice.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']:
            max_percent = max(invoice.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
            if invoice.currency_id.name == 'PEN':
                detration = self.my_round(self.my_round(self.amount_total_signed * (max_percent/100.0), 2), 0)
            else:
                detration = self.my_round(self.amount_total * (max_percent/100.0), 2)
        restante = float(invoice.amount_total) - detration
        return restante

    def action_post(self):
        res = super(AccountInvoice, self).action_post()
        for invoice in self:
            if invoice.move_type == 'out_invoice':
                if invoice.invoice_cred:
                    invoice.invoice_cred.unlink()
                vals = self.env['account.edi.xml.ubl_pe']._get_invoice_payment_terms_vals_list(invoice)
                credito = [item for item in vals if 'Credito' in item['payment_means_id']]
                cuotas = [item for item in vals if 'Cuota' in item['payment_means_id']]
                if credito and cuotas:
                    residuary = credito[0]['amount']
                    for line in cuotas:
                        residuary -= line['amount']
                        value = {'number_due': line['payment_means_id'],
                                 'amount_due': line['amount'],
                                 'amount_net': abs(residuary),
                                 'expiration_date': line['payment_due_date'],
                                 'account_move_credit': invoice.id}
                        self.env['account.invoice.credit'].create(value)
        return res

    @api.depends('invoice_cred')
    def compute_count_invoice_cred(self):
        for line in self:
            if len(line.invoice_cred) > 0:
                line.count_invoice_cred = True
            else:
                line.count_invoice_cred = False

    def my_round(self, n, ndigits):
        part = n * 10 ** ndigits
        delta = part - int(part)
        if delta >= 0.5 or -0.5 < delta <= 0:
            part = math.ceil(part)
        else:
            part = math.floor(part)
        return part / (10 ** ndigits)


class AccountInvoiceCredit(models.Model):
    _name = 'account.invoice.credit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Account invoice credit'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Activo', default=True)
    account_move_credit = fields.Many2one('account.move', string='Asiento contable')
    currency_credit = fields.Many2one('res.currency', string='Moneda', related='account_move_credit.currency_id')
    amount_due = fields.Float(string='Monto de cuota')
    amount_net = fields.Float(string='Monto Pendiente')
    expiration_date = fields.Date(string='Fecha de expiración')
    number_due = fields.Char(string='Numero de cuota')
    sequence = fields.Integer(string='Secuencia', default=10)


