from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'l10n_latam.identification.type'

    code_sirett = fields.Integer()
