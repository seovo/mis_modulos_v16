from odoo import fields, models


class CIIU(models.Model):
    _name = "l10n_cr.ciiu"
    _description = "CR CIIU"

    name = fields.Char(
        # required=True,
        # index=True,
    )
    code = fields.Char(
        # required=True,
        # index=True,
    )
    level = fields.Char()
