# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rmv = fields.Float(string="RMV", related='company_id.rmv', readonly=False)
    uit = fields.Float(string="UIT", related='company_id.uit', readonly=False)
    insurance_stop = fields.Float(string="MONTO DEL TOPE DE AFP SEGURO", related='company_id.insurance_stop', readonly=False)
    method_type = fields.Selection(string="Tipo de Método", related='company_id.method_type', readonly=False)
