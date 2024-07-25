from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit       = 'sale.order'

    def open_product_wizard_variant(self):
        return {
            "name": f"AGREGAR PRODUCTO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            #"view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "product.wizard.variantr",
            #"res_id": self.id,
            "target": "new",

        }