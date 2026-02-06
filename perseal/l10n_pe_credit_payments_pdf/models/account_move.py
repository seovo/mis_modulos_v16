from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _payment_credit(self):
        return True