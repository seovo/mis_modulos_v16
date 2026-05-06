from odoo import api, fields, models
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):

        limit_credit = self.partner_id.credit_limit

        if self.partner_id.parent_id:
            limit_credit = self.partner_id.parent_id.credit_limit

        if limit_credit != 0 :
            today = date.today()

            partner_ids = [self.partner_id.id]

            if self.partner_id.parent_id:
                partner_ids.append(self.partner_id.parent_id.id)



            moves = self.env['account.move'].search([
                ('partner_id','in',partner_ids)
                ('invoice_date_due', '<', today),
                ('state', '=', 'posted'),
                ('invoice_payment_state', '=', 'not_paid'),
                ('company_id','=',self.company_id.id)
            ])

            raise ValueError(moves)

        res = super().action_confirm()

        return res

