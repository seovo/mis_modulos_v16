import base64
from email.policy import default
import unicodedata
import os
import time
import io
from io import StringIO
from datetime import datetime, timedelta
from odoo import fields, api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class KadexElectronicoLine(models.Model):
     _name = 'kardex.electronico.sunat.line'
     _description = 'detalle del kardex'

     sequence = fields.Integer(string="Sequence", default=1, index=True, readonly=True)
     line = fields.Char(string='Linea')
     kardex_id = fields.Many2one('kardex.electronico.sunat', string="Kardex ID")
     period = fields.Char(string='Periodo', required=True)
     cuo = fields.Char(string='2-CUO', required=True)
     number_correlative_cuo = fields.Char(string='Numero Correlativoe CUO',required=True)
     code_establishment = fields.Char(string='Codigo Establecimiento ',required=True)
     code_table13 = fields.Char(string='Codigo Catalogo Sunat',required=True)
     type_exist = fields.Char(string='Tipo Existencia',required=True)
     code_exist = fields.Char(string='Codigo Propio Existencia',required=True)
     code_exist_catg13 = fields.Char(string='Código del catálogo utilizado')
     code_exist_CUB = fields.Char(string='Codigo Existencia CUB')
     date_document_issue = fields.Date(string='Fecha de Emision del Documento',required=True)
     type_document_transfer_intern = fields.Char(string='Tipo de Documento de Traslado')
     number_serie = fields.Char(string='Serie')
     number_document_transfer = fields.Char(string='Numero de Documento Interno')
     type_operation = fields.Char(string='Tipo Operacion Efectuada',required=True)
     description_exist = fields.Char(string='-Descripcion Existencia')
     code_uom_sunat = fields.Char(string='Codigo Unidad de Medida')
     code_metod_valuation = fields.Char(string='Codigo Metodo Valuacion')
     stock_quantity_in = fields.Char(string='Cantidad Entrada')
     unit_cost_in = fields.Char(string='Costo Unitario Entrada')
     cost_total_in = fields.Char(string='Costo Total Entrada')
     stock_quantity_out = fields.Char(string='Cantidad Salida')
     unit_cost_out = fields.Char(string='Costo Unitario Salida')
     cost_total_out = fields.Char(string='Costo Total Salida')
     unit_quantity_final = fields.Char(string='Cantidad Saldo Final')
     cost_unit_final = fields.Char(string='Costo Unitario Saldo Final')
     cost_total_final = fields.Char(string='Costo Total Saldo Final')
     state_operation = fields.Selection(string='Estado de la Operacion', selection=[('1', 'Pertenece al Periodo'),
                                                                                     ('8', 'NO anotado en Periodo anterior'), 
                                                                                     ('9', 'Anotado en Periodo anterior')])
     other = fields.Char(string='Otros')
     
