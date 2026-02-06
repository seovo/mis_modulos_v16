# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Report142xlxs(models.AbstractModel):
    _name = 'report.report.ple.14.2'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'report ple simplifide 14'

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
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 5)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 35)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 10)
        sheet.set_column('O:O', 10)
        sheet.set_column('P:P', 10)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 15)

        sheet.set_row(6, 30)
        sheet.set_row(7, 25)
        sheet.set_row(8, 30)

        sheet.merge_range('A1:D1', u'FORMATO 14.2: REGISTRO DE VENTAS E INGRESOS SIMPLIFICADO', bold_right)
        #sheet.merge_range('A3:B3', u'PERIODO: {}'.format(obj.range_id.name), bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),bold_right)
        sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL REGISTRO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n Y/O PAGO', bold)
        sheet.merge_range('D7:F7', u'COMPROBANTE DE PAGO \nO DOCUMENTO', bold)
        sheet.merge_range('D8:D9', u'TIPO', bold)
        sheet.merge_range('E8:E9', u'Nº SERIE', bold)
        sheet.merge_range('F8:F9', u'NÚMERO', bold)
        sheet.merge_range('G7:I7', u'INFORMACION DEL CLIENTE', bold)
        sheet.merge_range('G8:H8', u'DOCUMENTO DE IDENTIDAD', bold)
        sheet.write('G9', u'TIPO', bold)
        sheet.write('H9', u'NUMERO', bold)
        sheet.merge_range('I8:I9', u'APELLIDOS Y NOMBRES,\nDENOMINACION \nO RAZON SOCIAL', bold)
        sheet.merge_range('J7:J9', u'BASE \nIMPONIBLE \nDE LA \nOPERACIÓN \nGRAVADA', bold)
        sheet.merge_range('K7:K9', u'IGV Y/O IPM', bold)
        sheet.merge_range('L7:L9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        sheet.merge_range('M7:M9', u'IMPORTE\nTOTAL DEL \nCOMPROBANTE \nDE PAGO', bold)
        sheet.merge_range('N7:N9', u'TIPO DE \nCAMBIO', bold)
        sheet.merge_range('O7:R7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        sheet.merge_range('O8:O9', u'FECHA', bold)
        sheet.merge_range('P8:P9', u'TIPO', bold)
        sheet.merge_range('Q8:Q9', u'SERIE', bold)
        sheet.merge_range('R8:R9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)
        sheet.merge_range('S8:S9', u'ESTADO', bold)

        i = 9
        for line in obj.line_ids:
            sheet.write(i, 0, line.move_name, normal)
            sheet.write(i, 1, line.date_emission, normal)
            sheet.write(i, 2, line.date_due, normal)
            sheet.write(i, 3, line.document_payment_type, normal)
            sheet.write(i, 4, line.document_payment_series or '', normal)
            sheet.write(i, 5, line.document_payment_number or '', normal)
            sheet.write(i, 6, line.customer_document_type or '', normal)
            sheet.write(i, 7, line.customer_document_number or '', normal)
            sheet.write(i, 8, line.customer_name, left)
            sheet.write(i, 9, line.amount_untaxed or '0.00', right)
            sheet.write(i, 10, line.amount_tax_igv or '0.00', right)
            sheet.write(i, 11, line.amount_tax_other or '0.00', right)
            sheet.write(i, 12, line.amount_total or '0.00', right)
            sheet.write(i, 13, line.exchange_currency, right)
            sheet.write(i, 14, line.date_emission_update, normal)
            sheet.write(i, 15, line.document_payment_type_update, normal)
            sheet.write(i, 16, line.document_payment_series_update, normal)
            sheet.write(i, 17, line.document_payment_correlative_update, normal)
            sheet.write(i, 18, line.state_opportunity, normal)
            i += 1

