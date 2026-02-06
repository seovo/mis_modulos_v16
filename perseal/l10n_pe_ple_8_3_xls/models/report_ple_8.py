# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class Report08xlxs(models.AbstractModel):
    _name = 'report.report.ple.08.3'
    _description = 'report ple 8.3'
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
        # sheet.set_column('F:F', 20)
        sheet.set_column('F:F', 50)
        sheet.set_column('G:G', 5)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 50)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        # sheet.set_column('M:M', 15)
        # sheet.set_column('N:N', 15)
        # sheet.set_column('O:O', 15)
        # sheet.set_column('P:P', 15)
        # sheet.set_column('Q:Q', 20)
        # sheet.set_column('R:R', 10)
        sheet.set_column('M:M', 10)
        sheet.set_column('N:N', 10)
        sheet.set_column('O:O', 25)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 10)
        sheet.set_column('R:R', 10)
        sheet.set_column('S:S', 10)
        sheet.set_column('T:T', 5)
        sheet.set_column('U:U', 15)
        sheet.set_column('V:V', 20)

        sheet.set_row(6, 30)
        sheet.set_row(7, 30)
        sheet.set_row(8, 30)

        sheet.merge_range('A1:B1', u'FORMATO 8.3: "REGISTRO DE COMPRAS SIMPLIFICADO"', bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),bold_right)
        sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL ASIENTO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n O FECHA', bold)
        sheet.merge_range('D7:E7', u'COMPROBANTE DE PAGO O DOCUMENTO', bold)
        sheet.merge_range('D8:D9', u'TIPO', bold)
        sheet.merge_range('E8:E9', u'SERIE O CODIGO DE LA \nDEPENDENCIA ADUANERA', bold)
        # sheet.merge_range('F8:F9', u'AÑO DE EMISION DE \nLA DUA O DSI', bold)#
        sheet.merge_range('F7:F9', u'''Nº DEL COMPROBANTE DE PAGO, DOCUMENTO, \nNº DE ORDEN DEL FORMULARIO FISICO O 
        VIRTUAL,\nNº DE DUA, DSI O \nLIQUIDACION DE COBRANZA \nU OTROS DOCUMENTOS\n EMITIDOS POR SUNAT PARA ACREDITAR\n 
        EL CREDITO FISCAL EN LA IMPORTACION''', bold)
        sheet.merge_range('G7:I7', u'INFORMACION DEL PROVEDOOR', bold)
        sheet.merge_range('G8:H8', u'DOCUMENTO \nDE IDENTIDAD', bold)
        sheet.write('G9', u'TIPO', bold)
        sheet.write('H9', u'NUMERO', bold)
        sheet.merge_range('I8:I9', u'APELLIDOS Y NOMBRES,\nDENOMINACION O \nRAZON SOCIAL', bold)

        sheet.merge_range('J7:K8', u'ADQUISICIONES GRAVADAS \nDESTINADAS A OPERACIONES \nGRAVADAS Y/O EXPORTACIONES',bold)
        sheet.write('J9', u'BASE \nIMPONIBLE', bold)
        sheet.write('K9', u'IGV', bold)
        sheet.merge_range('L7:L9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        sheet.merge_range('M7:M9', u'IMPORTE\nTOTAL', bold)
        sheet.merge_range('N7:N9', u'Nº DE COMPROBANTE \nDE PAGO EMITIDO \nPOR SUJETO \nNO DOMICILIADO', bold)
        sheet.merge_range('O7:P7', u'CONSTANCIA DE DEPOSITO \nDE DETRACCION', bold)
        sheet.merge_range('O8:O9', u'NUMERO', bold)
        sheet.merge_range('P8:P9', u'FECHA DE \nEMISION', bold)
        sheet.merge_range('Q7:Q9', u'TIPO DE \nCAMBIO', bold)
        sheet.merge_range('R7:U7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        sheet.merge_range('R8:R9', u'FECHA', bold)
        sheet.merge_range('S8:S9', u'TIPO', bold)
        sheet.merge_range('T8:T9', u'SERIE', bold)
        sheet.merge_range('U8:U9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)

        # sheet.merge_range('S7:S9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        # sheet.merge_range('T7:T9', u'IMPORTE\nTOTAL', bold)
        # sheet.merge_range('U7:U9', u'Nº DE COMPROBANTE \nDE PAGO EMITIDO \nPOR SUJETO \nNO DOMICILIADO', bold)
        # sheet.merge_range('V7:W7', u'CONSTANCIA DE DEPOSITO \nDE DETRACCION', bold)
        # sheet.merge_range('V8:V9', u'NUMERO', bold)
        # sheet.merge_range('W8:W9', u'FECHA DE \nEMISION', bold)
        # sheet.merge_range('X7:X9', u'TIPO DE \nCAMBIO', bold)
        # sheet.merge_range('Y7:AB7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        # sheet.merge_range('Y8:Y9', u'FECHA', bold)
        # sheet.merge_range('Z8:Z9', u'TIPO', bold)
        # sheet.merge_range('AA8:AA9', u'SERIE', bold)
        # sheet.merge_range('AB8:AB9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)

        i = 9
        for line in obj.line_ids:
            sheet.write(i, 0, line.move_name, normal)
            sheet.write(i, 1, line.date_emission, normal)
            sheet.write(i, 2, line.date_due, normal)
            sheet.write(i, 3, line.document_payment_type, normal)
            sheet.write(i, 4, line.document_payment_series, normal)
            sheet.write(i, 5, line.document_payment_number, normal)
            sheet.write(i, 6, line.supplier_document_type, normal)
            sheet.write(i, 7, line.supplier_document_number, normal)
            sheet.write(i, 8, line.supplier_name, normal)
            sheet.write(i, 9, round(line.amount_untaxed1, 2) or '0.00', normal)
            sheet.write(i, 10, round(line.amount_tax_igv1, 2) or '0.00', normal)
            sheet.write(i, 11, round(line.amount_tax_other, 2) or '0.00', normal)
            sheet.write(i, 12, round(line.amount_total, 2) or '0.00', normal)
            sheet.write(i, 13, "", normal)
            sheet.write(i, 14, line.number_detraction, normal)
            sheet.write(i, 15, line.date_detraction, normal)
            sheet.write(i, 16, line.exchange_currency, normal)
            sheet.write(i, 17, line.date_emission_update, normal)
            sheet.write(i, 18, line.document_payment_type_update, normal)
            sheet.write(i, 19, line.document_payment_series_update, normal)
            sheet.write(i, 20, line.document_payment_correlative_update, normal)
            i += 1