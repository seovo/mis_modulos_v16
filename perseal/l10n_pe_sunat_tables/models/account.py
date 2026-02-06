# -*- coding: utf-8 -*-
from odoo import api, fields, models

MEDIUM_PAYMENT = [('001', 'DEPÓSITO EN CUENTA'),
                    ('002', 'GIRO'),
                    ('003', 'TRANSFERENCIA DE FONDOS'),
                    ('004', 'ORDEN DE PAGO'),
                    ('005', 'TARJETA DE DÉBITO'),
                    ('006', 'TARJETA DE CRÉDITO'),
                    ('007', 'CHEQUES CON LA CLÁUSULA DE "NO NEGOCIABLE", "INTRANSFERIBLES", "NO A LA ORDEN" U OTRA EQUIVALENTE, A QUE SE REFIERE EL INCISO F) DEL ARTICULO 5° DEL DECRETO LEGISLATIVO.'),
                    ('008', 'EFECTIVO, POR OPERACIONES EN LAS QUE NO EXISTE OBLIGACIÓN DE UTILIZAR MEDIOS DE PAGO'),
                    ('009', 'EFECTIVO, EN LOS DEMÁS CASOS'),
                    ('010', 'MEDIOS DE PAGO DE COMERCIO EXTERIOR'),
                    ('011', 'LETRAS DE CAMBIO'),
                    ('101', 'TRANSFERENCIAS - COMERCIO EXTERIOR'),
                    ('102', 'CHEQUES BANCARIOS - COMERCIO EXTERIOR'),
                    ('103', 'ORDEN DE PAGO SIMPLE - COMERCIO EXTERIOR'),
                    ('104', 'ORDEN DE PAGO DOCUMENTARIO - COMERCIO EXTERIOR'),
                    ('105', 'REMESA SIMPLE - COMERCIO EXTERIOR'),
                    ('106', 'REMESA DOCUMENTARIA - COMERCIO EXTERIOR'),
                    ('107', 'CARTA DE CRÉDITO SIMPLE - COMERCIO EXTERIOR'),
                    ('108', 'CARTA DE CRÉDITO DOCUMENTARIO - COMERCIO EXTERIOR'),
                    ('999', 'OTROS MEDIOS DE PAGO(ESPECIFICAR)')]


class account_journal(models.Model):
    _inherit = "account.journal"

    medium_payment = fields.Selection(MEDIUM_PAYMENT, string='Medio de pago')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    journal_type = fields.Selection(related='journal_id.type', string="journal Type")
    medium_payment = fields.Selection(MEDIUM_PAYMENT, string='Medio de pago')


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    journal_type = fields.Selection(related='journal_id.type')
    medium_payment = fields.Selection(MEDIUM_PAYMENT, string='Medio de pago')

    @api.onchange('journal_id')
    def _onchange_medium_payment(self):
        if self.journal_id:
            self.medium_payment = self.journal_id.medium_payment

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.medium_payment:
            res['medium_payment'] = self.medium_payment
        return res


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.depends('journal_id', 'partner_id', 'company_id', 'move_type')
    def _compute_l10n_latam_available_document_types(self):
        self.l10n_latam_available_document_type_ids = False
        for rec in self.filtered(lambda x: x.journal_id and x.partner_id):
            rec.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search(rec._get_l10n_latam_documents_domain())







