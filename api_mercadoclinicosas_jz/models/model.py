from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import string
import secrets
import time


class WebServices(models.Model):
    _name = "clinicos.web.services"
    _description = "clinicos.web.services"
    name = fields.Char(required=True)
    token = fields.Char(required=True)
    active = fields.Boolean(default=True)