from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    patent_id = fields.Many2one(
        comodel_name="l10n_cr.patent",
        readonly=True,
    )

    def action_view_patent(self):
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "l10n_cr.patent",
            "res_id": self.patent_id.id,
            "target": "current",
        }
