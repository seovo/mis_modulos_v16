from odoo import fields, models


class SucursalesToys(models.Model):
    _name = 'sucursales.toys'
    _description  = 'sucursales.toys'
    name = fields.Char()
    user_notify_ids = fields.Many2many('res.users')
