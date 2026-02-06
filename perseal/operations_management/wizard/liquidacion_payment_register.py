# -*- coding: utf-8 -*-
from locale import currency

from odoo import Command, models, fields, api, _


class LiquidacionPaymentRegister(models.TransientModel):
    _name = 'liquidacion.payment.register'
    _description = 'Register Payment'

    partner_id = fields.Many2one('res.partner', string='Partner')
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one(comodel_name='account.journal' ,string='Diario')
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method')
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False)
    source_amount = fields.Float(string='Total debt')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    communication = fields.Char(string="Memo", store=True, readonly=False,)
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Recipient Bank Account",
        readonly=False,
        store=True,
    )

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        line_ids = self.journal_id._get_available_payment_method_lines('inbound')
        if line_ids:
            self.payment_method_line_id = line_ids[0]
        else:
            self.payment_method_line_id = False
        if self.partner_id.bank_ids:
            self.partner_bank_id = self.partner_id.bank_ids[0]
        else:
            self.partner_bank_id = False
            
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        if self.env.company.currency_id != self.currency_id:
            self.amount = self.env.company.currency_id._convert(self.source_amount, self.currency_id, self.env.company, self.payment_date)
        else:
            self.amount = self.source_amount


    def action_create_payment(self):
        context = self._context
        data = {'partner_id': context.get('partner_id', False),
                'payment_type': 'outbound',
                'amount':self.amount,
                'currency_id': self.currency_id.id,
                'journal_id': self.journal_id.id,
                'payment_method_line_id': self.payment_method_line_id.id,
                'ref': self.communication,
        }
        if context['active_model'] in ['res.partner','operacion.documento']:
            data['payment_type'] = 'inbound'
        payment = self.env['account.payment'].create(data)
        payment.action_post()
        if context['active_model'] == 'res.partner':
            for line in self.partner_id.document_pending_ids.filtered(lambda l: l.register_payment):
                line.update({'payment_ids': [(4, payment.id, 0)]})
                payment.update({'documento_ids': [(4, line.id, 0)]})
                line.operacion_line_id.update({'date_of_pay':self.payment_date})
                line._compute_payment_count()
        elif context['active_model'] == 'operacion.documento':
            for line in self.env[context['active_model']].browse(context['active_ids']):
                line.update({'payment_ids': [(4, payment.id, 0)]})
                payment.update({'documento_ids': [(4, line.id, 0)]})
                line.operacion_line_id.update({'date_of_pay':self.payment_date})
                line._compute_payment_count()
        else:
            liquidacion = self.env[context['active_model']].browse(context['active_ids'])
            liquidacion.update({'payment_ids':[(4,payment.id,0)]})



