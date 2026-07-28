from odoo import models, fields


class LogsSirettSucursal(models.Model):
    _name = 'logs.sirett.sucursal'
    _description = 'logs.sirett.sucursal'
    date = fields.Datetime()
    note = fields.Text()
    sucursal_id = fields.Many2one('stock.sucursal.sirett')
    type = fields.Selection([('new','Nuevos'),('update','Update')])