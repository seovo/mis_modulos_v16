from odoo import api, fields, models
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    acquisition_cost = fields.Float(string="Costo de adquisición")
    acq_exchange_rate = fields.Float(string="Tipo de cambio de adquisición")


class ProductCategory(models.Model):
    _inherit = 'product.category'
    supplier_disc = fields.Float(string="Descuento %")




class AccountMove(models.Model):
    _inherit = 'account.move'
    inv_exchange_rate_display = fields.Float(default=1)