# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    teletransfer = fields.Boolean(string='Usado en teletransfer')
