# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    detraction_account_id = fields.Many2one('account.account',
                                            string='Cuenta de detraccion',
                                            related='company_id.detraction_account_id',
                                            readonly=False)