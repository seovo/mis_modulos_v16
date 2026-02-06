# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'


    @api.depends('restrict_mode_hash_table', 'state','edi_document_ids.state')
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            move.show_reset_to_draft_button = (
                    not move.restrict_mode_hash_table \
                    and (move.state == 'cancel' or (move.state == 'posted' and not move.need_cancel_request))
            )
        for move in self:
            for doc in move.edi_document_ids:
                move_applicability = doc.edi_format_id._get_move_applicability(move)
                if doc.edi_format_id._needs_web_services() \
                        and doc.state in ('sent', 'to_cancel') \
                        and move_applicability \
                        and move_applicability.get('cancel'):
                    move.show_reset_to_draft_button = False
                    break