from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def compute_payments_widget_reconciled_info(self):
        self._compute_payments_widget_reconciled_info()