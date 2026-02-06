from odoo import models, fields, api, _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    l10n_pe_edi_refund_reason = fields.Selection(selection_add=[('13', 'Corrección del monto neto pendiente de pago'
                                                                       ' y/o la(s) fechas(s) de vencimiento del pago'
                                                                       ' único o de las cuotas y/o los montos'
                                                                       ' correspondientes a cada cuota de ser el caso')])

    def reverse_moves(self, is_modify=False):
        res = super(AccountMoveReversal, self).reverse_moves(is_modify)
        if self.l10n_pe_edi_refund_reason =='13':
            if self._context.get('active_id'):
                invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
                invoice_refund_id = self.env['account.move'].browse(res['res_id'])
                if invoice_refund_id.move_type == 'out_refund':
                    invoice_refund_id.write({'invoice_payment_term_id': invoice_id.invoice_payment_term_id.id})
                    if invoice_id.invoice_cred:
                        for cuota in invoice_id.invoice_cred:
                            vals = {
                                'number_due': cuota.number_due,
                                'amount_due': cuota.amount_due,
                                'amount_net': cuota.amount_net,
                                'expiration_date': cuota.expiration_date,
                                'account_move_credit': invoice_refund_id.id,
                            }
                            self.env['account.invoice.credit'].create(vals)
        return res