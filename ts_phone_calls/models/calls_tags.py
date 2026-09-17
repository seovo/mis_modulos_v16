from odoo import api, exceptions, fields, models


class CallsTags(models.Model):
    _name = 'calls.tags'

    name = fields.Char(string="Call Tag Name")