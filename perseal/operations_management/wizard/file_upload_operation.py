# -*- coding: utf-8 -*-

import base64
import xlrd

from odoo import api, fields, models
from odoo.exceptions import UserError


class CargaNotaDebito(models.TransientModel):
    _name = "file.upload.operation"
    _description = "Carga de archivos operaciones"

    archivo = fields.Binary(string="Archivo (*.xlsx)")
    nombre_archivo = fields.Char(string="Nombre del archivo")

    def action_upload_file(self):
        decoded_data = base64.decodebytes(self.archivo)
        wb = xlrd.open_workbook(file_contents=decoded_data)
        worksheet = wb.sheet_by_index(0)
        docuemnto_obj = self.env['operacion.documento']
        operacion_id = self.env['operacion.operacion'].browse(self._context.get('active_id'))
        operacion_lines = []
        for fila in range(1, worksheet.nrows):
            if worksheet.cell(fila, 4).value:
                issue_date = xlrd.xldate.xldate_as_datetime(worksheet.cell(fila, 4).value, wb.datemode).date()
            else:
                issue_date = False
            if worksheet.cell(fila, 5).value:
                disbursement_date = xlrd.xldate.xldate_as_datetime(worksheet.cell(fila, 5).value, wb.datemode).date()
            else:
                disbursement_date = False
            if worksheet.cell(fila, 6).value:
                due_date = xlrd.xldate.xldate_as_datetime(worksheet.cell(fila, 5).value, wb.datemode).date()
            else:
                due_date = False
            num_documento = worksheet.cell(fila, 2).value.split('-')

            values = {'tipo_documento_id': self.env['l10n_latam.document.type'].search([('name', '=', worksheet.cell(fila, 1).value)], limit=1).id or False,
                      'name': worksheet.cell(fila, 2).value,
                      'num_documento': num_documento[1] + '-' + num_documento[2],
                      'proveedor_id': self.env['res.partner'].search([('name', '=', worksheet.cell(fila, 3).value)], limit=1).id or False,
                      'issue_date': issue_date,
                      'disbursement_date': disbursement_date,
                      'due_date': due_date,
                      'cedente_id': self.env['res.partner'].search([('name', '=', worksheet.cell(fila, 7).value)], limit=1).id or False,
                      'deudor_id': self.env['res.partner'].search([('name', '=', worksheet.cell(fila, 8).value)], limit=1).id or False,
                      'currency_id': self.env['res.currency'].search([('name', '=', worksheet.cell(fila, 9).value)],limit=1).id or False,
                      'net_amount_document': float(worksheet.cell(fila, 10).value),
                      'company_id': self.env['res.company'].search([('name', '=', worksheet.cell(fila, 11).value)],limit=1).id or False,
                      }
            document_id = docuemnto_obj.create(values)
            dict_operacion_line = {'monto_neto': float(worksheet.cell(fila, 10).value),
                                   'documento_id': document_id.id}
            operacion_lines.append((0, 0, dict_operacion_line))
        operacion_id.update({'line_ids': operacion_lines})





