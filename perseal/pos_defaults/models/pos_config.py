# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    default_partner = fields.Many2one(
        comodel_name='res.partner',
        string=_('Default Customer'),
    )