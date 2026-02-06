# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    account_credit_id = fields.Many2one(comodel_name='account.account', string=_('Account Credit'))
    account_debit_id = fields.Many2one(comodel_name='account.account', string=_('Account Debit'))