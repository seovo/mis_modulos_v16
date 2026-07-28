from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    alias = fields.Char(string="Alias")
    condition = fields.Selection(
        selection=[
            ("inactive", "Inactive"),
            ("active", "Active"),
        ],
        string="Condición"
    )
    taxpayer = fields.Boolean(string="Contribuyente")
    outstanding = fields.Float(
        string="Pendiente de Pago",
        help="Monto pendiente de pago asociado al socio.",
        readonly=False,  # Permitir edición
        store=True,  # Hacerlo almacenable
    )
