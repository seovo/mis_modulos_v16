# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_pe_edi_provider_url = fields.Char(
        string="Nubefact Url",
        related="company_id.l10n_pe_edi_provider_url",
        readonly=False)
    l10n_pe_edi_provider_token = fields.Char(
        string="Nubefact Token",
        related="company_id.l10n_pe_edi_provider_token",
        readonly=False)
