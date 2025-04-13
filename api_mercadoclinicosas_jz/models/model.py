from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import string
import secrets
import time

class Website(models.Model):
    _inherit = 'website'
    show_app =  fields.Boolean()

class WebServices(models.Model):
    _name = "clinicos.web.services"
    _description = "clinicos.web.services"
    name = fields.Char(required=True)
    token = fields.Char(required=True)
    active = fields.Boolean(default=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self,vals):
        #raise ValueError('HOLAAA')
        res = super().create(vals)
        return res

    #website