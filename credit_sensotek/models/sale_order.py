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

            moves = self.env['account.move'].search([
                ('invoice_date_due', '<', today),
                ('state', '=', 'posted'),
                ('invoice_payment_state', '=', 'not_paid')
            ])

            raise ValueError(moves)

        res = super().action_confirm()

        return res

