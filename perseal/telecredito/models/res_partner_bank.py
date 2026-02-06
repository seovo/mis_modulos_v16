# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    acc_cci_number = fields.Char(string='CCI')