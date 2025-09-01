from odoo import api, fields, models
import io
try:
    import base64
except:
    install('base64')

try:
    import xlsxwriter
except:
    install('xlsxwriter')

class ReportScheduleLand(models.TransientModel):
    _name = "report.schedule.land"
    _description  = "report.schedule.land"
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def do_excell(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/binary/download_excell_report_schedule_land/{self.company_id.id}',
            'target': 'self',
        }

    def get_report_xls(self,company):
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        sheet = workbook.add_worksheet()
        self.get_report_xls_data(workbook, sheet,company)
        workbook.close()
        excel_file = base64.encodebytes(fp.getvalue())
        fp.close()
        return excel_file

    def get_report_xls_data(self,workbook, sheet,company):


        xc = 1

        bold = workbook.add_format({'bold': True})
        format_body = workbook.add_format(
            {'bold': False, 'align': 'center', 'valign': 'vcenter', 'bottom': 2, 'top': 2, 'left': 2, 'right': 2})

        sheet.write(xc, 1, 'EXPEDIENTE', bold)
        sheet.write(xc, 2, 'MZ', bold)
        sheet.write(xc, 3, 'LOTE', bold)
        sheet.write(xc, 4, 'NOMBRE DE CLIENTE', bold)
        sheet.write(xc, 5, 'METRAJE', bold)
        sheet.write(xc, 6, 'FECHA DE COBRANZA', bold)
        sheet.write(xc, 7, 'FECHA PAGADA / HOY', bold)
        sheet.write(xc, 8, 'DIAS VENCIDOS', bold)
        sheet.write(xc, 9, 'N° CUOTA', bold)
        sheet.write(xc, 10, 'MONTO', bold)
        sheet.write(xc, 11, 'ETAPA', bold)
        sheet.write(xc, 10, 'EMPRESA', bold)
        sheet.write(xc, 10, 'COMPROBANTE DE CUOTA', bold)
        sheet.write(xc, 10, 'FECHA DE EMISION', bold)
        sheet.write(xc, 10, 'ESTADO', bold)

        xc += 1


        schedule_dues = self.env['schedule.dues.land'].search([('order_id.company_id','=',company.id)])

        for schedule_due in schedule_dues:

            order = schedule_due.order_id

            invoice_pagada = str(schedule_due.invoice_date) if schedule_due.invoice_date else fields.Datetime.date().now()

            sheet.write(xc, 1, schedule_due.nro_internal_land, format_body)
            sheet.write(xc, 2, order.mz_land, format_body)
            sheet.write(xc, 3, order.lot_land, format_body)
            sheet.write(xc, 4, order.partner_id.display_name, format_body)
            sheet.write(xc, 5, order.m2_land, format_body)
            sheet.write(xc, 6, str(schedule_due.date), format_body)
            sheet.write(xc, 7, invoice_pagada , format_body)
            sheet.write(xc, 8, 'DIAS VENCIDOS', format_body)
            sheet.write(xc, 9, 'N° CUOTA', format_body)
            sheet.write(xc, 10, 'MONTO', format_body)
            sheet.write(xc, 11, 'ETAPA', format_body)
            sheet.write(xc, 10, 'EMPRESA', format_body)
            sheet.write(xc, 10, 'COMPROBANTE DE CUOTA', format_body)
            sheet.write(xc, 10, 'FECHA DE EMISION', format_body)
            sheet.write(xc, 10, 'ESTADO', format_body)

            xc +=  1





