from odoo import api, exceptions, fields, models


class CallsSummary(models.Model):
    _name = 'calls.summary'

    name = fields.Char(string="Call Summary Name")