from odoo import api, fields, models , _

class SellerLand(models.Model):
    _name          = 'seller.land'
    _description   = 'seller.land'
    name           = fields.Char()
    commission_percentage          = fields.Float()


