# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class Report08xlxs(models.AbstractModel):
    _name = 'report.report.ple.08'
    _description = 'report ple 8'
    _inherit ='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('{}.xlsx'.format(obj.filename_txt))
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

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 5)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 50)
        sheet.set_column('H:H', 5)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 50)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 10)
        sheet.set_column('S:S', 10)
        sheet.set_column('T:T', 10)
        sheet.set_column('U:U', 25)
        sheet.set_column('V:V', 15)
        sheet.set_column('W:W', 10)
        sheet.set_column('X:X', 10)
        sheet.set_column('Y:Y', 10)
        sheet.set_column('Z:Z', 5)
        sheet.set_column('AA:AA', 15)
        sheet.set_column('AB:AB', 20)

        sheet.set_row(6, 30)
        sheet.set_row(7, 30)
        sheet.set_row(8, 30)

        sheet.merge_range('A1:B1', u'FORMATO 8.1: "REGISTRO DE COMPRAS"', bold_right)
        #sheet.merge_range('A3:B3', u'PERIODO: {}'.format(obj.range_id.name), bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),
                          bold_right)

        sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL ASIENTO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n O FECHA', bold)
        sheet.merge_range('D7:F7', u'COMPROBANTE DE PAGO O DOCUMENTO', bold)
        sheet.merge_range('D8:D9', u'TIPO', bold)
        sheet.merge_range('E8:E9', u'SERIE O CODIGO DE LA \nDEPENDENCIA ADUANERA', bold)
        sheet.merge_range('F8:F9', u'AÑO DE EMISION DE \nLA DUA O DSI', bold)
        sheet.merge_range('G7:G9', u'''Nº DEL COMPROBANTE DE PAGO, DOCUMENTO, \nNº DE ORDEN DEL FORMULARIO FISICO O 
        VIRTUAL,\nNº DE DUA, DSI O \nLIQUIDACION DE COBRANZA \nU OTROS DOCUMENTOS\n EMITIDOS POR SUNAT PARA ACREDITAR\n 
        EL CREDITO FISCAL EN LA IMPORTACION''', bold)
        sheet.merge_range('H7:J7', u'INFORMACION DEL PROVEDOOR', bold)
        sheet.merge_range('H8:I8', u'DOCUMENTO \nDE IDENTIDAD', bold)
        sheet.write('H9', u'TIPO', bold)
        sheet.write('I9', u'NUMERO', bold)
        sheet.merge_range('J8:J9', u'APELLIDOS Y NOMBRES,\nDENOMINACION O \nRAZON SOCIAL', bold)

        sheet.merge_range('K7:L8', u'ADQUISICIONES GRAVADAS \nDESTINADAS A OPERACIONES \nGRAVADAS Y/O EXPORTACIONES',
                          bold)
        sheet.write('K9', u'BASE \nIMPONIBLE', bold)
        sheet.write('L9', u'IGV', bold)

        sheet.merge_range('M7:N8', u'ADQUISICIONES GRAVADAS \nDESTINADAS A OPERACIONES '
                                   u'\nGRAVADAS Y/O EXPORTACION Y \nA OPERACIONES NO GRAVADAS', bold)
        sheet.write('M9', u'BASE \nIMPONIBLE', bold)
        sheet.write('N9', u'IGV', bold)

        sheet.merge_range('O7:P8', u'ADQUISICION GRAVADAS \nDESTINADAS A OPERACIONES \nNO GRAVADAS', bold)
        sheet.write('O9', u'BASE \nIMPONIBLE', bold)
        sheet.write('P9', u'IGV', bold)

        sheet.merge_range('Q7:Q9', u'VALOR DE LAS \nADQUISICIONES \nNO GRAVADAS', bold)
        sheet.merge_range('R7:R9', u'ISC', bold)
        sheet.merge_range('S7:S9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        sheet.merge_range('T7:T9', u'IMPORTE\nTOTAL', bold)
        sheet.merge_range('U7:U9', u'Nº DE COMPROBANTE \nDE PAGO EMITIDO \nPOR SUJETO \nNO DOMICILIADO', bold)

        sheet.merge_range('V7:W7', u'CONSTANCIA DE DEPOSITO \nDE DETRACCION', bold)
        sheet.merge_range('V8:V9', u'NUMERO', bold)
        sheet.merge_range('W8:W9', u'FECHA DE \nEMISION', bold)

        sheet.merge_range('X7:X9', u'TIPO DE \nCAMBIO', bold)

        sheet.merge_range('Y7:AB7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        sheet.merge_range('Y8:Y9', u'FECHA', bold)
        sheet.merge_range('Z8:Z9', u'TIPO', bold)
        sheet.merge_range('AA8:AA9', u'SERIE', bold)
        sheet.merge_range('AB8:AB9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)

        i = 9
        for line in obj.line_ids:
            sheet.write(i, 0, line.move_name, normal)
            sheet.write(i, 1, line.date_emission, normal)
            sheet.write(i, 2, line.date_due, normal)
            sheet.write(i, 3, line.document_payment_type, normal)
            sheet.write(i, 4, line.document_payment_series, normal)
            sheet.write(i, 5, line.date_dua, normal)
            sheet.write(i, 6, line.document_payment_number, normal)
            sheet.write(i, 7, line.supplier_document_type, normal)
            sheet.write(i, 8, line.supplier_document_number, normal)
            sheet.write(i, 9, line.supplier_name, normal)
            sheet.write(i, 10, round(line.amount_untaxed1, 2) or '0.00', normal)
            sheet.write(i, 11, round(line.amount_tax_igv1, 2)or '0.00', normal)
            sheet.write(i, 12, round(line.amount_untaxed2, 2) or '0.00', normal)
            sheet.write(i, 13, round(line.amount_tax_igv2, 2) or '0.00', normal)
            sheet.write(i, 14, round(line.amount_untaxed3, 2) or '0.00', normal)
            sheet.write(i, 15, round(line.amount_tax_igv3, 2) or '0.00', normal)
            sheet.write(i, 16, round(line.amount_exo, 2) or '0.00', normal)
            sheet.write(i, 17, round(line.amount_tax_isc, 2) or '0.00', normal)
            sheet.write(i, 18, round(line.amount_tax_other, 2) or '0.00', normal)
            sheet.write(i, 19, round(line.amount_total, 2) or '0.00', normal)
            sheet.write(i, 20, "", normal)
            sheet.write(i, 21, line.number_detraction, normal)
            sheet.write(i, 22, line.date_detraction, normal)
            sheet.write(i, 23, line.exchange_currency, normal)
            sheet.write(i, 24, line.date_emission_update, normal)
            sheet.write(i, 25, line.document_payment_type_update, normal)
            sheet.write(i, 26, line.document_payment_series_update, normal)
            sheet.write(i, 27, line.document_payment_correlative_update, normal)
            i += 1