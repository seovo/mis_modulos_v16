from odoo import api, fields, models , _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.depends('move_ids')
    def _compute_from_moves(self):
        res = super()._compute_from_moves()
        res.update({
            'l10n_pe_edi_cancel_reason':  self.reason
        })
        return res