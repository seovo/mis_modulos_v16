from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'l10n_latam.identification.type'
    code_sirett = fields.Integer()


class L10n_latamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'
    code_sirett = fields.Integer()
