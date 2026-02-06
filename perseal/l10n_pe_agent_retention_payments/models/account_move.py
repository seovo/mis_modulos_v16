# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_restante(self, invoice):
        restante = super(AccountMove, self).get_restante(invoice)
        retention = invoice._prepare_retention()
        if retention:
            if 'Amount' in retention:
                restante = restante - retention['Amount']
        return restante