# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class Report08xlxs(models.AbstractModel):
    _name = 'report.report.ple.06.1'
    _inherit ='report.report_xlsx.abstract'
    _description = 'Report ple 6.1'

    def generate_xlsx_report(self, workbook, data, obj):
        ws = workbook.add_worksheet('Libro Mayor')
        titulo1 = workbook.add_format(
            {'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name': 'Arial'})
        titulo_1 = workbook.add_format(
            {'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name': 'Arial'})
        titulo_2 = workbook.add_format(
            {'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name': 'Arial'})
        titulo2 = workbook.add_format(
            {'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'color': 'black', 'text_wrap': True, 'left': True,
             'right': True, 'bottom': True, 'top': True, 'bold': True, 'font_name': 'Arial'})
        titulo_3 = workbook.add_format({'font_size': 8, 'font_name': 'Arial', 'bold': True})
        letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name': 'Arial'})
        number_right = workbook.add_format(
            {'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Arial'})

        ws.set_column('A:A', 2, letter1)
        ws.set_column('B:B', 24, letter1)
        ws.set_column('C:C', 11.5, letter1)
        ws.set_column('D:D', 30, letter1)
        ws.set_column('E:E', 11, letter1)
        ws.set_column('F:F', 13, letter1)
        ws.set_column('G:G', 13, letter1)
        ws.set_column('H:H', 13, letter1)
        ws.set_column('I:I', 11.5, number_right)
        ws.set_column('J:J', 11.5, number_right)
        ws.set_column('K:K', 11.5, number_right)
        ws.set_column('L:L', 9, number_right)

        ws.merge_range('B1:E1', 'FORMATO 6.1: LIBRO MAYOR', titulo1)

        ws.write(2, 1, 'PERIODO:', titulo_1)
        ws.write(3, 1, 'RUC:', titulo_1)
        ws.merge_range('B5:D5', 'APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', titulo_1)
        ws.write(3, 2, obj.company_id.vat or '', titulo_2)

        ws.write(2, 2, self._periodo_fiscal(obj.date_from) or '', titulo_2)
        ws.merge_range('E5:I5', obj.company_id.name or '', titulo_2)


        ws.write(5, 1, 'FECHA', titulo2)
        ws.write(5, 2, 'NÚMERO', titulo2)
        ws.write(5, 3, 'DESCRIPCIÓN DE LA OPERACIÓN', titulo2)
        ws.merge_range('F6:G6', 'DOCUMENTO REFERENCIA', titulo2)
        ws.write(5, 7, 'CÓDIGO', titulo2)
        ws.merge_range('I6:J6', 'MOVIMIENTO', titulo2)
        ws.write(5, 9, '', titulo2)
        ws.write(6, 1, 'OPERACIÓN', titulo2)
        ws.write(6, 2, 'COMPROBANTE', titulo2)
        ws.write(6, 3, '', titulo2)
        ws.write(6, 4, 'TD', titulo2)
        ws.write(6, 5, 'NÚMERO', titulo2)
        ws.write(6, 6, 'FECHA', titulo2)
        ws.write(6, 7, 'ANEXO', titulo2)
        ws.write(6, 8, 'DEBE', titulo2)
        ws.write(6, 9, 'HABER', titulo2)
        row = 7

        for line in obj.line_ids:
            ws.write(row, 1, line.fecha_operacion, titulo_1)
            ws.write(row, 2, (len(line.num_serie_comprobante_pago or '') != 0) * (
                        str(line.num_serie_comprobante_pago or '') + '-' + str(line.num_comprobante_pago or '')), titulo_1)
            ws.write(row, 3, line.glosa or '', titulo_1)
            ws.write(row, 4, line.tipo_comprobante_pago or '', titulo_1)
            ws.write(row, 5, "%s-%s" % (line.num_serie_comprobante_pago or "", line.num_comprobante_pago or "") or '',
                     titulo_1)
            ws.write(row, 6, line.fecha_contable, titulo_1)
            ws.write(row, 7, line.num_doc_iden_emisor or '', titulo_1)
            ws.write(row, 8, line.movimientos_debe or 0.00)
            ws.write(row, 9, line.movimientos_haber or 0.00)
            row += 1


    def _periodo_fiscal(sefl,date):
        # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
        return '{}{}'.format(str(fields.Date().from_string(date).year),
                             str(fields.Date().from_string(date).month).rjust(2, "0"))


