from odoo import api, fields, models , _

class SellerLand(models.Model):
    _name          = 'seller.land'
    _description   = 'seller.land'

    active         = fields.Boolean(default=True)
    name           = fields.Char()
    commission_percentage          = fields.Float()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


