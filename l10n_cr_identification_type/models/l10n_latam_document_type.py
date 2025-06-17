# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class L10nLatamDocumentType(models.Model):

    _inherit = 'l10n_latam.document.type'

    notes = fields.Char('Notes')
