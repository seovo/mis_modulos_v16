from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):

        if len(self) == 1 :
            if self.type == 'out_invoice' :
                limit_credit = self.partner_id.credit_limit

                if self.partner_id.parent_id:
                    limit_credit = self.partner_id.parent_id.credit_limit

                if limit_credit != 0:
                    today = date.today()

                    partner_ids = [self.partner_id.id]

                    if self.partner_id.parent_id:
                        partner_ids.append(self.partner_id.parent_id.id)

                    moves = self.env['account.move'].search([
                        ('id','!=',self.id) ,
                        ('type', '=', 'out_invoice'),
                        ('partner_id', 'in', partner_ids),
                        ('invoice_date_due', '<', today),
                        ('state', '=', 'posted'),
                        ('invoice_payment_state', '=', 'not_paid'),
                        ('company_id', '=', self.company_id.id)
                    ])

                    amount_residual_signed = 0

                    for move in moves:
                        amount_residual_signed += move.amount_residual_signed

                    monto_actual = self.amount_total

                    moneda_venta = self.currency_id
                    moneda_compañia = self.company_id.currency_id

                    if moneda_compañia != moneda_venta:
                        monto_actual = moneda_venta._convert(monto_actual, moneda_compañia,
                                                             self.company_id or self.env.company,
                                                             self.invoice_date or fields.Date.today())

                    sum_total = monto_actual + amount_residual_signed

                    sum_total = round(sum_total, 2)

                    excede_limit = limit_credit < sum_total

                    if excede_limit:
                        msg = f"El cliente {self.partner_id.display_name}  ah excedido el limite de credito ({limit_credit})"
                        msg += f"tiene una deuda de {amount_residual_signed} + el valor de venta actual {monto_actual} "
                        msg += f"sumando un total de credito de  {sum_total} "

                        raise UserError(msg)

        res = super().action_post()



        return res