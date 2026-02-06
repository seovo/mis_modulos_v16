# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    have_target_account = fields.Boolean(_('Tener cuenta objetivo'))
    target_account_debit = fields.Many2one('account.account', string=_('Débito de la cuenta de destino'),
                                           help="Target account debit.")
    target_account_credit = fields.Many2one('account.account', string=_('Crédito de la cuenta objetivo'),
                                            help="Target account credit .")