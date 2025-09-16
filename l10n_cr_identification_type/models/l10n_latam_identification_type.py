# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class L10nLatamIdentificationType(models.Model):

    _inherit = 'l10n_latam.identification.type'
    doc_code_prefix = fields.Char()
    report_name = fields.Char()
    code = fields.Char()
