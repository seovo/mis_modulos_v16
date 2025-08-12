from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    advance_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta para Pagos por Adelantado",
    )
