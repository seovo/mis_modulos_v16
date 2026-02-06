# -*- coding: utf-8 -*-
import io
import os
import base64
import zipfile
from lxml import etree
from datetime import timedelta, datetime
from jinja2 import FileSystemLoader, Environment
from odoo import osv, models, fields, api, _, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

path_dir = os.path.dirname(os.path.realpath(__file__))
loader = FileSystemLoader(os.path.join(path_dir, './'))
env = Environment(loader=loader)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    tabla10 = fields.Many2one('catalog.element', string='Tipo de Documento', domain=[('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10')])
    tabla12 = fields.Many2one('catalog.element', string='Operación Sunat', domain=[('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12')])
    number_document = fields.Char(string='Numero de documento')
    enable_document = fields.Boolean(string='habilitar documento', compute='get_enable_document')
    # is_guie = fields.Boolean(string='Es guia')

    @api.depends('move_ids_without_package')
    def get_enable_document(self):
        for pick in self:
            enable = True

            for move in pick.move_ids_without_package:
                if move.purchase_line_id:
                    if move.purchase_line_id.invoice_lines:
                        enable = False

                if move.sale_line_id:
                    if move.sale_line_id.invoice_lines:
                        enable = False
                        break
            pick.enable_document = enable
        return



class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    sequence_guia_id = fields.Many2one('ir.sequence', string='Secuencia para la guia')