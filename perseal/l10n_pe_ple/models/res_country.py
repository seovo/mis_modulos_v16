# -*- coding: utf-8 -*-

from odoo import models, fields, _


class res_country(models.Model):
    _inherit = 'res.country'

    code_sunat = fields.Char(
        string=_('Sunat Code'), size=4,
        help=_('Sunat Code for countries reported in Electronic Invoicing')
    )