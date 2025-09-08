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

try:
    import tempfile
except:
    install('tempfile')

import os



class ReportScheduleLand(models.TransientModel):
    _name = "report.schedule.land"
    _description  = "report.schedule.land"
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def print_report_schedule_excell(self,order):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/binary/download_excell_report_schedule_land_order/{order.id}',
            'target': 'self',
        }



    def do_excell(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/binary/download_excell_report_schedule_land/{self.company_id.id}',
            'target': 'self',
        }

    def get_report_xls(self,company,sale=None):
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        sheet = workbook.add_worksheet()
        if sale:
            self.get_report_xls_data_sale(workbook, sheet,sale)
        else:
            self.get_report_xls_data(workbook, sheet,company)


        workbook.close()
        excel_file = base64.encodebytes(fp.getvalue())
        fp.close()
        return excel_file

    def get_report_xls_data_sale(self,workbook, sheet,order):

        xc = 1

        ##HEADER
        bold = workbook.add_format({'bold': True , 'align': 'center', 'valign': 'vcenter' })
        format_body = workbook.add_format({
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'bottom': 2, 'top': 2, 'left': 2, 'right': 2
        })
        bg_azul_text_white = workbook.add_format({
            'bg_color': '#003366', 'border': 1 , 'bold': True ,
            'align': 'center', 'valign': 'vcenter' , 'color': 'white'
        })
        bg_azulwhite_bold = workbook.add_format({
            'bg_color': '#449ef8ff', 'border': 1 , 'bold': True ,
            'align': 'center', 'valign': 'vcenter'
        })

        #sheet.write(xc, 1, 'REPORTE  CUOTAS', bold)
        sheet.merge_range('B1:G1', 'REPORTE CUOTAS', bg_azul_text_white)
        xc += 1

        sheet.write(xc, 1, 'MZ-LT:', bold)
        sheet.merge_range('C1:G1', order.partner_id.display_name, bg_azul_text_white)
        xc += 1


        sheet.write(xc, 1, 'DESCRIPCION', bold)
        sheet.write(xc, 2, 'ABONADO', bold)
        sheet.write(xc, 3, 'FECHA DE CUOTA', bold)
        sheet.write(xc, 4, 'N° OP', bold)
        sheet.write(xc, 5, 'N° BOLETA / FACTURA', bold)
        sheet.set_column('B:F', 15)

        sheet.write(xc, 6, 'COMPROBANTE', bold)
        sheet.set_column('G:G', 30)

        xc += 1


        schedule_dues = self.env['schedule.dues.land'].search([
            ('order_id','=',order.id)
        ])

        for schedule_due in schedule_dues:
            move = schedule_due.move_id

            OPS = []

            for pago in schedule_due.move_id.bank_origin_ids:
                OPS.append(pago.operation_number)

            OPS = ','.join(OPS) if OPS else ''

            sheet.write(xc, 1, schedule_due.description, format_body)
            sheet.write(xc, 2, schedule_due.amount_due_land, format_body)
            sheet.write(xc, 3, str(schedule_due.invoice_date or '') , format_body)
            sheet.write(xc, 4, OPS, format_body)
            sheet.write(xc, 5, schedule_due.move_id.display_name or '', format_body)


            for attach in move.attachment_ids:
                contador = 6
                if 'image' in attach.mimetype:
                    #sheet.write(xc, 1, attach.datas, format_body)

                    # Decodificar el contenido Base64
                    image_data = base64.b64decode(attach.datas)

                    # Guardar la imagen en un archivo temporal
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_file.write(image_data)
                        temp_file_path = temp_file.name

                    # Insertar la imagen en la hoja de cálculo
                    #sheet.insert_image(xc, contador, temp_file_path)

                    image_width = 10  # ancho en píxeles
                    image_height = 10  # altura en píxeles

                    #sheet.insert_image(xc, contador, temp_file_path, {'x_scale': 0.5, 'y_scale': 0.5})
                    sheet.insert_image(xc, contador, temp_file_path, {'x_scale': image_width / 100, 'y_scale': image_height / 100})
                    #os.remove(temp_file_path)
                    # Ajustar la altura de la celda
                    sheet.set_row(xc, 100)  # Establecer la altura de la fila

                    #xc += 1
                    contador += 1

            xc += 1






    def get_report_xls_data(self,workbook, sheet,company):


        xc = 1

        bold = workbook.add_format({'bold': True , 'align': 'center', 'valign': 'vcenter' })
        format_body = workbook.add_format(
            {'bold': False, 'align': 'center', 'valign': 'vcenter', 'bottom': 2, 'top': 2, 'left': 2, 'right': 2})

        # Definir el formato para las celdas coloreadas
        format_red = workbook.add_format({
          'bg_color': '#FFCCCC',  # Color de fondo (rojo claro)
          'font_color': '#000000',  # Color de texto (negro)
          'bold': True ,  # Opcional: texto en negrita ,
          'align': 'center', 'valign': 'vcenter'
        })




        sheet.write(xc, 1, 'EXPEDIENTE', bold)
        sheet.set_column('B:B', 20)

        sheet.write(xc, 2, 'MZ', bold)
        sheet.write(xc, 3, 'LOTE', bold)
        sheet.set_column('C:D', 15)


        sheet.write(xc, 4, 'NOMBRE DE CLIENTE', bold)
        sheet.set_column('E:E', 50)

        sheet.write(xc, 5, 'METRAJE', bold)
        sheet.set_column('F:F', 15)

        sheet.write(xc, 6, 'FECHA DE COBRANZA', bold)
        sheet.set_column('G:G', 20)

        sheet.write(xc, 7, 'FECHA PAGADA / HOY', bold)
        sheet.set_column('H:H', 20)

        sheet.write(xc, 8, 'DIAS VENCIDOS', bold)
        sheet.write(xc, 9, 'N° CUOTA', bold)
        sheet.write(xc, 10, 'MONTO', bold)
        sheet.write(xc, 11, 'ETAPA', bold)
        sheet.set_column('I:L', 15)

        sheet.write(xc, 12, 'EMPRESA', bold)
        sheet.set_column('M:M', 50)

        sheet.write(xc, 13, 'COMPROBANTE DE CUOTA', bold)
        sheet.set_column('N:N', 25)

        sheet.write(xc, 14, 'FECHA DE EMISION', bold)
        sheet.set_column('O:O', 20)

        sheet.write(xc, 15, 'ESTADO', bold)
        sheet.set_column('P:P', 15)


        xc += 1


        schedule_dues = self.env['schedule.dues.land'].search([
            ('order_id.company_id','=',company.id),('type_schedule','=','dues')
        ])

        for schedule_due in schedule_dues:

            order = schedule_due.order_id

            invoice_pagada = schedule_due.invoice_date if schedule_due.invoice_date else fields.Datetime.now().date()

            sheet.write(xc, 1, schedule_due.nro_internal_land, format_body)
            sheet.write(xc, 2, order.mz_land, format_body)
            sheet.write(xc, 3, order.lot_land, format_body)
            sheet.write(xc, 4, order.partner_id.display_name, format_body)
            sheet.write(xc, 5, order.m2_land, format_body)
            sheet.write(xc, 6, str(schedule_due.date), format_body)
            sheet.write(xc, 7, str(invoice_pagada) , format_body)
            sheet.write(xc, 8, (invoice_pagada - schedule_due.date ).days , format_body)
            sheet.write(xc, 9, schedule_due.number_due, format_body)
            sheet.write(xc, 10, schedule_due.amount_due_land , format_body)
            sheet.write(xc, 11, order.sector_land, format_body)
            sheet.write(xc, 12, order.company_id.display_name, format_body)
            sheet.write(xc, 13, schedule_due.move_id.display_name, format_body)
            sheet.write(xc, 14, str(schedule_due.invoice_date or '') , format_body)

            if schedule_due.is_paid:
                sheet.write(xc, 15, 'CANCELADO', format_red)
            else:
                sheet.write(xc, 15, 'PENDIENTE', format_body)

            xc +=  1





