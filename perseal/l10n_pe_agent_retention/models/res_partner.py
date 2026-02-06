# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_retention = fields.Boolean(string='Agente Retención SUNAT')
    percent_retention = fields.Float(
        string='Porcentaje de Retención %',
        default=3,
    )
