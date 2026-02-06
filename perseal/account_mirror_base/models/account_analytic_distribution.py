# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountAnalyticDistribution(models.Model):
    _inherit = 'account.analytic.distribution'
    
    account_credit_id = fields.Many2one(comodel_name='account.account', string=_('Account Credit'))
    account_debit_id = fields.Many2one(comodel_name='account.account', string=_('Account Debit'))
    
    
