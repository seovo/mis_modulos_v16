# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self, is_modify=False):
        res = super(AccountMoveReversal, self).reverse_moves(is_modify)
        # if self.refund_method in ['refund', 'cancel']:
        if res.get('res_id', False):
            move_id = self.env['account.move'].browse(res['res_id'])
            document_type_id = self.env['l10n_latam.document.type'].sudo().search([
                ('code', '=', '07'),
                ('doc_code_prefix', '=', move_id.journal_id.code[0:1])
            ])
            if document_type_id and move_id.move_type not in ['out_invoice', 'in_invoice']:
                move_id.write({'l10n_latam_document_type_id': document_type_id.id})
            move_id._compute_name()
        return res