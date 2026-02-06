from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    def _get_rate_date(self):
        self.ensure_one()
        if self.move_id.move_type in ('out_refund', 'in_refund') and self.move_id.reversed_entry_id:
            return self.move_id.reversed_entry_id.invoice_date or self.move_id.reversed_entry_id.date or fields.Date.context_today(self)
        else:
            return self.move_id.invoice_date or self.move_id.date or fields.Date.context_today(self)