# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string=_('Journal Invoice Account'), readonly=True
    )
    def _order_fields(self, ui_order):
        fields = super()._order_fields(ui_order)
        fields['invoice_journal_id'] = ui_order['invoice_journal_id'] if 'invoice_journal_id' in ui_order else False
        return fields

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if self.invoice_journal_id:
            vals.update({'journal_id': self.invoice_journal_id.id,
                         'l10n_latam_document_type_id': self.invoice_journal_id.l10n_pe_document_type_id.id})
        return vals



    #
    # def _prepare_invoice_vals(self):
    #     res = super(PosOrder, self)._prepare_invoice_vals()
    #     # res.update({'journal_id': 19})
    #     if self.invoice_journal_id:
    #         res.update({'journal_id': self.invoice_journal_id.id})
    #         if self.invoice_journal_id.l10n_latam_use_documents:
    #             res.update({'l10n_latam_document_type_id': self.invoice_journal_id.l10n_pe_document_type_id.id})
    #     return res
    #
    #
    # @api.model
    # def _order_fields(self, ui_order):
    #     res = super(PosOrder, self)._order_fields(ui_order)
    #     # res.update({'invoice_journal_id': 19})
    #     if 'invoice_journal_id' in ui_order:
    #         res.update({'invoice_journal_id': ui_order.get('invoice_journal_id', False)})
    #     return res

