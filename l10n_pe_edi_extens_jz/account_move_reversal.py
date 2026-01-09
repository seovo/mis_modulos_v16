from odoo import api, fields, models , _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    @api.depends('move_ids', 'journal_id')
    def _compute_documents_info(self):
        res = super()._compute_documents_info()

        for record in self:

            if record.l10n_latam_available_document_type_ids and len(record.move_ids) == 1:
                move = record.move_ids

                if move.l10n_latam_document_type_id and move.move_type in ['out_invoice']:
                    for dtypes in record.l10n_latam_available_document_type_ids:
                        if dtypes.doc_code_prefix == move.l10n_latam_document_type_id.doc_code_prefix:
                            record.l10n_latam_available_document_type_ids = [(6, 0, dtypes.ids)]



        return res


    def _prepare_default_reversal(self, move):
        """ Set the default document type and number in the new revsersal move taking into account the ones selected in
        the wizard """
        res = super()._prepare_default_reversal(move)
        res.update({
            'l10n_pe_edi_cancel_reason':  self.reason
        })
        return res

