# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class ReportReportPle053xlxs(models.AbstractModel):
    _name = 'report.report.ple.05.3'
    _description = 'Report ple 5.3'
    _inherit ='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        ws = workbook.add_worksheet('{}.xlsx'.format(obj.filename_txt))
        bold_right = workbook.add_format({'bold': True, 'font_color': 'black'})
        bold = workbook.add_format({'bold': True, 'font_color': 'black'})
        normal = workbook.add_format({'font_color': 'black'})
        right = workbook.add_format({'font_color': 'black'})
        left = workbook.add_format({'font_color': 'black'})
        bold.set_align('center')
        bold.set_text_wrap()
        normal.set_align('center')
        left.set_align('left')
        right.set_align('right')
        ws.set_column('A:A', 2, normal)
        ws.set_column('B:B', 20, normal)
        ws.set_column('C:C', 20, normal)
        ws.set_column('D:D', 20, normal)
        ws.set_column('E:E', 40, normal)
        ws.set_column('F:F', 20, normal)
        ws.set_column('G:G', 40, normal)
        ws.set_column('H:H', 20, normal)
        ws.set_column('I:I', 40, normal)
        ws.merge_range('B1:E1', 'FORMATO 5.3: LIBRO DIARIO - DETALLE DE PLAN CONTABLE UTILIZADO', bold_right)
        ws.write(2, 1, 'PERIODO:', bold_right)
        ws.write(3, 1, 'RUC:', bold_right)
        ws.merge_range('B5:D5', 'APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', bold_right)
        ws.write(3, 2, obj.company_id.vat or '', bold)
        ws.merge_range('E5:I5', obj.company_id.name or '', bold)
        ws.write(2, 2, self._periodo_fiscal(obj.date_from) or '', bold)
        ws.merge_range("B7:B8", 'ESTADO O INDICADOR', bold)
        ws.merge_range("C7:C8", 'FECHA \nDE LA OPERACIÓN', bold)
        ws.merge_range("D7:E7", 'CUENTA CONTABLE', bold)
        ws.merge_range('F7:G7', 'PLAN DE CUENTAS UTILIZADO POR EL DEUDOR TRIBUTARIO', bold)
        ws.merge_range('H7:I7', 'CUENTA CONTABLE CORPORATIVA', bold)
        ws.write(7, 3, 'CÓDIGO', bold)
        ws.write(7, 4, 'DESCRIPCIÓN', bold)
        ws.write(7, 5, 'CÓDIGO', bold)
        ws.write(7, 6, 'DESCRIPCIÓN', bold)
        ws.write(7, 7, 'CÓDIGO', bold)
        ws.write(7, 8, 'DESCRIPCIÓN', bold)
        ws.freeze_panes(8, 0)
        fila = 8
        for line in obj.line_ids:
            ws.write(fila, 1, '1', normal)
            ws.write(fila, 2, line.period, normal)
            ws.write(fila, 3, line.codigo_cuenta_desagregado, right)
            ws.write(fila, 4, line.descripcion_cuenta_desagregado, normal)
            ws.write(fila, 5, line.codigo_cuenta_tributario, right)
            ws.write(fila, 6, line.descripcion_cuenta_tributario, normal)
            ws.write(fila, 7, line.codigo_cuenta_corporativa, right)
            ws.write(fila, 8, line.descripcion_cuenta_corporativa, normal)
            fila += 1

    def _periodo_fiscal(sefl, date):
        # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
        return '{}{}'.format(str(fields.Date().from_string(date).year),
                             str(fields.Date().from_string(date).month).rjust(2, "0"))
