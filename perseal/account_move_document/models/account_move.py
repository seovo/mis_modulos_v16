# -*- coding: utf-8 -*-

from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    apertura = fields.Boolean(string='Diario de apertura')
    cierre = fields.Boolean(string='Diario de cierre')


class AccountMove(models.Model):
    _inherit = 'account.move'

    apertura = fields.Boolean(
        string='Diario de apertura',
        related='journal_id.apertura',
    )
    cierre = fields.Boolean(
        string='Diario de cierre',
        related='journal_id.cierre',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    documento = fields.Char(string='Documento')
