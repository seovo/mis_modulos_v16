from odoo import models, fields, api, _
from odoo.tools.float_utils import float_repr, float_round


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _prepare_amount_credit(self):
        amount_cuota = 0.00
        for invoice in self:
            if invoice.invoice_cred:
                for cuotas in invoice.invoice_cred:
                    amount_cuota+=cuotas.amount_due
        return amount_cuota