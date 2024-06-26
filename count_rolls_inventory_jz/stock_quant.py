from odoo import api, fields, models

class StockQuant(models.Model):
    _inherit       = 'stock.quant'
    qty_rolls  = fields.Float(string="Rollos")


class StockMOVE(models.Model):
    _inherit       = 'stock.move'
    qty_rolls  = fields.Float(string="Rollos")