from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit= 'account.move'

    l10n_latam_document_number = fields.Char(
        compute='_compute_l10n_latam_document_number', inverse='_inverse_l10n_latam_document_number',
        string='Document Number', readonly=True, store=True, states={'draft': [('readonly', False)]})
