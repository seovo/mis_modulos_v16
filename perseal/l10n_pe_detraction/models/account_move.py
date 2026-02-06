# -*- coding: utf-8 -*-

import math

from odoo import api, fields, models
from datetime import datetime
from odoo.tools.float_utils import float_repr, float_round


class AccountMove(models.Model):
    _inherit = "account.move"

    detraction_show = fields.Boolean(string='Mostrar de detracción')
    detraction_percentage = fields.Float(string='Porcentaje de detracción')
    detraction_amount = fields.Float(string='Monto de detracción (S/)')
    detraction_amount_spot = fields.Float(string='Monto de detracción')

    is_detraction_pay = fields.Boolean(string='Pago detracción',related='detraction_payment_id.is_detraction_pay')
    detraction_move_id = fields.Many2one('account.move', string="Asiento de detraccion")
    detraction_payment_id = fields.Many2one('account.payment', string="Pago de detraccion")
    detraction_operation_number = fields.Char(string='Nro detracción', related='detraction_payment_id.detraction_operation_number', readonly=False)
    detraction_operation_date = fields.Date(string='Fecha detracción', related='detraction_payment_id.detraction_operation_date', readonly=False)


    def action_register_payment(self):
        res = super(AccountMove, self).action_register_payment()
        res['context']['show_detraction'] = True
        if len(self) == 1:
            if self.detraction_amount > 0:
                res['context']['detraction_amount'] = self.detraction_amount
                res['context']['show_detraction'] = False
        return res

    @api.onchange(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.quantity',
        'invoice_line_ids.price_unit',
        'currency_id',
        'l10n_pe_edi_operation_type',
    )
    def onchange_compute_tax_totals(self):
        # super(AccountMove, self)._compute_tax_totals()
        if self.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']:
            self.detraction_show = True
        else:
            self.detraction_show = False
        self.onchange_l10n_pe_edi_operation_type()

    def onchange_l10n_pe_edi_operation_type(self):
        for move in self:
            detraction_amount = 0
            if move.move_type in ['out_invoice', 'in_invoice']:
                max_amount = 400 if '027' in move.invoice_line_ids.mapped('product_id.l10n_pe_withhold_code') else 700
                max_percent = max(move.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
                if move.company_id.currency_id.name == 'PEN':
                    if max_percent and abs(move.amount_total_signed) > max_amount and move.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']:
                        move.detraction_amount_spot = detraction_amount = round(move.amount_total * (max_percent / 100.0), 2)
                    if move.currency_id.name != 'PEN':
                        detraction_amount = move.currency_id._convert(detraction_amount, move.company_id.currency_id, move.company_id, move.invoice_date or datetime.today().strftime('%Y-%m-%d'))
                else:
                    currency_pen = self.env.ref('base.PEN')
                    amount_total_signed = move.company_id.currency_id._convert(abs(move.amount_total_signed), currency_pen, move.company_id, move.invoice_date or datetime.today().strftime('%Y-%m-%d'))
                    if max_percent and abs(amount_total_signed) > max_amount and move.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']:
                        move.detraction_amount_spot = detraction_amount = round(amount_total_signed * (max_percent / 100.0), 2)
                move.detraction_percentage = max_percent
                move.detraction_amount = abs(round(detraction_amount))

    def _l10n_pe_edi_get_detraction(self):
        return True

    def my_round(self, n, ndigits):
        part = n * 10 ** ndigits
        delta = part - int(part)
        if delta >= 0.5 or -0.5 < delta <= 0:
            part = math.ceil(part)
        else:
            part = math.floor(part)
        return part / (10 ** ndigits)

    def _l10n_pe_edi_get_spot(self):
        res = super(AccountMove, self)._l10n_pe_edi_get_spot()
        if not self.detraction_amount > 0:
            return {}
        if 'payment_percent' in res and 'spot_amount' in res and 'amount' in res:
            res['spot_amount'] = self.detraction_amount_spot
            res['amount'] = self.detraction_amount
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        for line in res:
            move_detract_id = self.env['account.move'].search([('name', '=', line.name), ('detraction_show', '=', True), ('detraction_amount', '>', 0)])
            for l in move_detract_id:
                if l.detraction_show and l.detraction_amount > 0:
                    l.detraction_move_id = line.move_id
        return res

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        super(AccountMoveLine, self)._compute_totals()
        self._origin.move_id.onchange_l10n_pe_edi_operation_type()
