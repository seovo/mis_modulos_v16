# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    rmv = fields.Float(string="RMV")
    uit = fields.Float(string="UIT")
    insurance_stop = fields.Float(string="MONTO DEL TOPE DE AFP SEGURO")
    method_type = fields.Selection([('1', 'Mensual'), ('2', 'Promedio')], string="Tipo de Método", default='1')