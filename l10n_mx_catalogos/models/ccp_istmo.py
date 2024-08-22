# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CcpRegistroIstmo(models.Model):
    _name = 'ccp.registro.istmo'
    _rec_name = "descripcion"

    clave = fields.Char(string='Clave')
    descripcion = fields.Char(string='Descripción')
