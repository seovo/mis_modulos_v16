# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    identification_id = fields.Many2one('l10n_latam.document.type', 'Document type')
