from odoo import fields, models


class PatentType(models.Model):
    _name = "l10n_cr.patent.type"
    _description = "CR Patent Type"

    name = fields.Char(
        required=True,
        index=True,
    )
    code = fields.Char(
        required=True,
        index=True,
    )
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        # default=lambda self: self.env.ref("l10n_cr_municipality.product_patent"),
        string="Pago de Patente",
    )
    product_advance_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        # default=lambda self: self.env.ref("l10n_cr_municipality.product_patent_advance"),
        string="Pago de Patente por Adelantado",
    )


    product_licor_id = fields.Many2one(
        comodel_name="product.product",
        required=False,
        # default=lambda self: self.env.ref("l10n_cr_municipality.product_patent"),
        string="Timbre Pantente Licor",
    )

