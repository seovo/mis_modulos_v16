# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CveParteTransporte(models.Model):
    _name = 'cve.parte.transporte'
    _rec_name = "descripcion"
    _description = 'cvepartetransporte'

    clave = fields.Char(string='Clave')
    descripcion = fields.Char(string='Descripción')
