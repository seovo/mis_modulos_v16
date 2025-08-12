from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    base_salary = fields.Float(
        string="Salario Base",
        config_parameter="l10n_cr.base_salary",
    )
    ntcs = fields.Float(
        string="NTcs",
        config_parameter="l10n_cr.ntcs",
    )
    vncs = fields.Float(
        string="VNcs",
        config_parameter="l10n_cr.vncs",
    )
    atcs = fields.Float(
        string="ATcs",
        config_parameter="l10n_cr.atcs",
    )
    payment_in_advance_discount = fields.Float(
        string="Descuento por pago adelantado",
        config_parameter="l10n_cr.payment_in_advance_discount",
    )
    advance_account_id = fields.Many2one(
        related="company_id.advance_account_id",
        readonly=False,
    )
