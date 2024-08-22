# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CcpCondEsp(models.Model):
    _name = 'ccp.condiciones.esp'
    _rec_name = "descripcion"

    clave = fields.Char(string='Clave')
    descripcion = fields.Char(string='Descripción')
