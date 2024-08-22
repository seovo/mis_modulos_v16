# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CcpRegimenAduanero(models.Model):
    _name = 'ccp.regimen.aduanero'
    _rec_name = "descripcion"

    clave = fields.Char(string='Clave')
    descripcion = fields.Char(string='Descripción')
