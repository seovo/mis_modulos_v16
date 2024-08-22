# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CcpTipoMateria(models.Model):
    _name = 'ccp.tipo.materia'
    _rec_name = "descripcion"

    clave = fields.Char(string='Clave')
    descripcion = fields.Char(string='Descripción')
