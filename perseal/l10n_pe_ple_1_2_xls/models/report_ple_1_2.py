# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ReportPle0101(models.AbstractModel):
    _name = 'report.report.ple.01.2'
    _description = 'Report ple 1.2'
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

        ws.set_column('A:A', 20)
        ws.set_column('B:B', 20)
        ws.set_column('C:C', 25)
        ws.set_column('D:D', 30)
        ws.set_column('E:E', 35)
        ws.set_column('F:F', 30)
        ws.set_column('G:G', 20)
        ws.set_column('H:H', 20)
        ws.set_column('I:I', 20)
        ws.set_column('J:J', 20)

        ws.set_row(6, 30)
        ws.set_row(7, 25)
        ws.set_row(8, 30)

        ws.merge_range('A1:D1', u'FORMATO 1.2: LIBRO CAJA Y BANCOS - DETALLE DE LOS MOVIMIENTOS DE LA CUENTA CORRIENTE', bold_right)
        ws.merge_range('A3:B3', u'PERIODO: {}'.format(self._periodo_fiscal(obj.date_from)), bold_right)
        ws.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        ws.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name), bold_right)

        ws.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL REGISTRO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        ws.merge_range('B7:B9', 'FECHA \nDE LA \nOPERACIÓN', bold)
        ws.merge_range('C7:F7', 'OPERACIONES BANCARIAS', bold)
        ws.merge_range('C8:C9', 'MEDIO DE PAGO', bold)
        ws.merge_range('D8:D9', 'DESCRIPCIÓN \nDE LA OPERACIÓN', bold)
        ws.merge_range('E8:E9', 'APELLIDOS Y NOMBRES, \nDENOMINACIÓN O RAZÓN SOCIAL', bold)
        ws.merge_range('F8:F9', 'NÚMERO DE \nTRANSACCIÓN BANCARIA', bold)
        ws.merge_range('G7:H7', 'CUENTA CONTABLE ASOCIADA', bold)
        ws.merge_range('G8:G9', 'CÓDIGO', bold)
        ws.merge_range('H8:H9', 'DENOMINACIÓN', bold)
        ws.merge_range('I7:J7', 'SALDOS Y MOVIMIENTOS', bold)
        ws.merge_range('I8:I9', 'DEUDOR', bold)
        ws.merge_range('J8:J9', 'ACREEDOR', bold)

        row = 9
        x = 1
        for line in obj.line_ids:
            ws.write(row, 0, x, normal)
            ws.write(row, 1, line.fecha_operacion, normal)
            ws.write(row, 2, line.medio_pago, normal)
            ws.write(row, 3, line.glosa, normal)
            ws.write(row, 4, line.partner_name, normal)
            ws.write(row, 5, line.num_transaccion_bancaria, normal)
            ws.write(row, 6, line.codigo_cuenta_desagregado_id.code, normal)
            ws.write(row, 7, line.codigo_cuenta_desagregado_id.name, normal)
            ws.write(row, 8, line.movimientos_debe, right)
            ws.write(row, 9, line.movimientos_haber, right)
            row += 1
            x += 1

    def _periodo_fiscal(sefl, date):
        # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
        return '{}{}'.format(str(fields.Date().from_string(date).year),
                             str(fields.Date().from_string(date).month).rjust(2, "0"))