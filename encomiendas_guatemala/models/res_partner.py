from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit       = 'res.partner'
    use_whatsapp = fields.Boolean(string='Tiene Wasap')
    file_vat     = fields.Binary(string="Adjunto Documento")
    name_file_vat     = fields.Char()

    def write(self,values):
        #raise ValueError(values)
        res = super().write(values)
        return res

class StockPicking(models.Model):
    _inherit       = 'stock.picking'

    @api.model
    def create(self,values):
        raise ValueError('okaa')
        res = super().create(values)
        return res