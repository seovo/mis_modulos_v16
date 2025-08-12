from odoo import fields, models, api, _
import json

class AccountMove(models.Model):
    _inherit = "account.move"

    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        readonly=True,
    )

    user_paid = fields.Many2one('res.users',string='Usuario que registro el pago',store=True,readonly=True,compute="compute_user_paid")

    @api.depends('move_type', 'line_ids.amount_residual')
    def compute_user_paid(self):
        for inv in self:
            if inv.invoice_payments_widget:
                objs = json.loads(inv.invoice_payments_widget)
                if objs:
                    if len(objs['content']) > 0:
                        pay_id = objs['content'][0]['account_payment_id']
                        payment = self.env['account.payment'].sudo().browse(pay_id)
                        if payment:
                            inv.user_paid = payment.create_uid

