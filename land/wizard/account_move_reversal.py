from odoo import api, fields, models , _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'


    def _prepare_default_reversal(self, move):
        """ Set the default document type and number in the new revsersal move taking into account the ones selected in
        the wizard """
        res = super()._prepare_default_reversal(move)
        res.update({
            'l10n_pe_edi_cancel_reason':  self.reason
        })
        return res

