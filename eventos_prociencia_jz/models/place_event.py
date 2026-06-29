from odoo import models, exceptions, fields , _

class PlaceEvent(models.Model):
    _name = "place.event"
    _description = "place.event"
    name = fields.Char(string="Lugar")
    address = fields.Char(string="Dirección")
    length  = fields.Float()
    latitude = fields.Float()