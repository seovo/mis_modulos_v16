# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        l10n_pe_edi_departure_start_date = self.l10n_pe_edi_departure_start_date
        picking = super().button_validate()
        self.l10n_pe_edi_departure_start_date = l10n_pe_edi_departure_start_date
        return picking

    @api.onchange('l10n_pe_edi_transport_type')
    def _onchange_l10n_pe_edi_transport_type(self):
        if self.l10n_pe_edi_transport_type in ['01', '02']:
            if self.fields_get().get('tabla10', False):
                if self.tabla10:
                    if self.tabla10.name in self.env['ir.model.fields'].search([('name', '=', 'l10n_pe_edi_related_document_type')]).selection_ids.mapped('value'):
                        self.l10n_pe_edi_related_document_type = self.tabla10.name
                    else:
                        self.l10n_pe_edi_related_document_type = False
                if self.number_document:
                    self.l10n_pe_edi_document_number = self.number_document