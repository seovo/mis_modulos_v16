# -*- coding: utf-8 -*-

from odoo import models, fields

class Producto(models.Model):
    """
    Define el modelo de Productos para el módulo de Datawave.
    """
    _name = 'datawave.producto'
    _description = 'Productos de Datawave'

    sku = fields.Char(string='SKU')
    name = fields.Char(string='Nombre', required=True)
    categ = fields.Char(string='Categoría')
    uom = fields.Char(string='Unidad de Medida')
    state = fields.Char(string='Estado')
