from odoo import fields, models


class Identification(models.Model):
    _name = "l10n_cr.identification"
    _description = "CR Identification"

    name = fields.Char()
