from odoo import _, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    preapproval_plan_id = fields.Char(string="Id Plan Mercado Pago")