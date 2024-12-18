from odoo import api, fields, models

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.onchange('move_ids')
    def change_journal_jz(self):
        for record in self:
            if len(record.move_ids) == 1:
                journal = record.move_ids.journal_id

                if journal.journal_reverse_jz:

                    #raise ValueError(code)
                    record.journal_id = journal.journal_reverse_jz.id



