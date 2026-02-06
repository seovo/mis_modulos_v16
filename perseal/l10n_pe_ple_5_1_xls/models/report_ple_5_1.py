# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class Report08xlxs(models.AbstractModel):
    _name = 'report.report.ple.05.1'
    _description = 'Report ple 5.1'
    _inherit ='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        ws = workbook.add_worksheet('Libro diario')
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
        ws.set_column('B:B', 24, normal)
        ws.set_column('C:C', 15, normal)
        ws.set_column('D:D', 30, normal)
        ws.set_column('E:E', 15, normal)
        ws.set_column('F:F', 20, normal)
        ws.set_column('G:G', 20, normal)
        ws.set_column('H:H', 20, normal)
        ws.set_column('I:I', 30, normal)
        ws.set_column('J:J', 15, right)
        ws.set_column('K:K', 15, right)
        ws.set_column('L:L', 10, right)

        ws.merge_range('B1:E1', 'FORMATO 5.1: LIBRO DIARIO', bold_right)

        ws.merge_range("B7:B8", 'NÚMERO CORRELATIVO \nDEL REGISTRO O \nCÓDIGO ÚNICO DE LA OPERACIÓN', bold)
        ws.merge_range("C7:C8", 'FECHA \nDE LA OPERACIÓN', bold)
        ws.merge_range("D7:D8", 'GLOSA O DESCRIPCIÓN \nDE LA OPERACIÓN', bold)

        ws.merge_range('E7:G7', 'REFERENCIA DE LA OPERACIÓN', bold)
        ws.write(7, 4, 'CÓDIGO DEL LIBRO O REGISTRO', bold)
        ## 7 , 8 , 9
        ws.write(7, 5, 'NÚMERO CORRELATIVO', bold)
        ws.write(7, 6, 'NÚMERO DEL DOCUMENTO SUSTENTATORIO', bold)

        ws.merge_range('H7:I7', 'CUENTA CONTABLE ASOCIADA A LA OPERACIÓN', bold)
        ws.write(7, 7, 'CÓDIGO', bold)
        ws.write(7, 8, 'DENOMINACIÓN', bold)
        ws.merge_range('J7:K7', 'MOVIMIENTO', bold)
        ws.write(7, 9, 'DEBE', bold)
        ws.write(7, 10, 'HABER', bold)

        ws.write(2, 1, 'PERIODO:', bold_right)
        ws.write(3, 1, 'RUC:', bold_right)
        ws.merge_range('B5:D5', 'APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', bold_right)
        ws.write(3, 2, obj.company_id.vat or '', bold)

        ws.write(2, 2, self._periodo_fiscal(obj.date_from) or '', bold)
        ws.merge_range('E5:I5', obj.company_id.name or '', bold)

        ws.freeze_panes(9, 0)

        fila = 8
        for line in obj.line_ids:
            ws.write(fila, 1, line.move_name,normal)
            ws.write(fila, 2, line.fecha_contable or '', normal)
            ws.write(fila, 3, line.glosa or '', normal)
            ws.write(fila, 4, "5", normal)
            ws.write(fila, 5, line.num_serie_comprobante_pago, normal)
            ws.write(fila, 6, (len(line.num_serie_comprobante_pago or '') != 0) * (str(line.num_serie_comprobante_pago or '') + '-' + str(line.num_comprobante_pago or '')) or line.num_comprobante_pago, normal)
            ws.write(fila, 7, line.codigo_cuenta_desagregado or '', normal)
            ws.write(fila, 8, line.codigo_cuenta_desagregado_id.name or '', normal)
            ws.write(fila, 9, line.movimientos_debe, normal)
            ws.write(fila, 10, line.movimientos_haber, normal)
            fila += 1

    def _periodo_fiscal(sefl,date):
        # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
        return '{}{}'.format(str(fields.Date().from_string(date).year),
                             str(fields.Date().from_string(date).month).rjust(2, "0"))
