from odoo import api, fields, models , _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update({
            'l10n_pe_edi_cancel_reason':  self.reason
        })
        return res