from odoo import api, Command, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_detraction_pay = fields.Boolean(string='Pago detracción?')
    detraction_operation_number = fields.Char(string='Nro detracción')
    detraction_operation_date = fields.Date(string='Fecha detracción')

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        if self.is_detraction_pay:
            account_invoice = self.env['account.move'].browse(self._context['active_id'])
            account_invoice.write({'detraction_payment_id': res.id,
                                   'detraction_move_id':res.move_id.id,
                                    'l10n_pe_detraction_number':self.detraction_operation_number,
                                    'l10n_pe_detraction_date':self.detraction_operation_date})
        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.is_detraction_pay:
            payment_vals.update({'is_detraction_pay': self.is_detraction_pay,
                                 'detraction_operation_number': self.detraction_operation_number,
                                 'detraction_operation_date': self.detraction_operation_date,
                                 'move_detraction_id': self._context['active_id']})
        return payment_vals

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id','payment_date', 'is_detraction_pay')
    def _compute_amount(self):
        for wizard in self:
            context = self._context
            if wizard.is_detraction_pay and context.get('detraction_amount'):
                if wizard.currency_id.name != 'PEN':
                    wizard.currency_id = self.env.company.currency_id
                wizard.amount = context.get('detraction_amount')

            else:
                if wizard.source_currency_id == wizard.currency_id:
                    wizard.amount = wizard.source_amount_currency
                elif wizard.currency_id == wizard.company_id.currency_id:
                    wizard.amount = wizard.source_amount
                else:
                    amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id, wizard.payment_date)
                    wizard.amount = amount_payment_currency
