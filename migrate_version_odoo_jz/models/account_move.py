from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'



    def set_compute_amount(self):
        self._compute_amount()