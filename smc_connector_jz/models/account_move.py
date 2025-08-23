from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    def send_smc_data(self):
        return

