from odoo import api, fields, models , _
from datetime import date
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

stage_payment_lan = {
    'separation' :'Separado',
    'initial'    :'Inicial Incompletada',
    'dues'       :'Cuotas Pendientes',
    'payment'    : 'Pagando Cuotas',
    'completed'  :'Cuotas Completada'
}

stage_land   = {
  'signed'       :'Firmado',
  'preaviso'     :'Carta Preaviso',
  'cancel'       :'Resuelto',
  'regularizado' :'Regularizado'
}

year_current = fields.Datetime.now().year


class ReportScheduleLand(models.TransientModel):
    _name         = "report.schedule.land"
    _description  = "report.schedule.land"
    company_id    = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    date_start    = fields.Date(string='Fecha Inicio Cuota')
    date_end    = fields.Date(string='Fecha Fin Cuota')
    balance_year = fields.Boolean(string='Balance Anual')

    year   = fields.Integer(default=year_current,string='Año')

    def print_report_schedule_excell(self,order):
        url = f'/web/binary/download_excell_report_schedule_land_order/{order.id}?start={self.date_start}&end={self.date_end}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }



    def do_excell(self):
        url =  f'/web/binary/download_excell_report_schedule_land/{self.company_id.id}?start={self.date_start}&end={self.date_end}&byear={self.balance_year}&year={self.year}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    def get_report_xls(self,company,sale=None,kw={}):
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        sheet = workbook.add_worksheet()

        domain = []

        continue_report = True


        if 'byear' in kw:
            if kw['byear'] == 'True':
                continue_report = False

                domain = [('state','=','sale'),('company_id','=',company.id)]

                orders = self.env['sale.order'].search(domain)

                self.get_report_xls_data_year(workbook, sheet,orders,int(kw['year']))


        if continue_report:
            if 'start' in kw:
                if kw['start'] and kw['start'] != 'False' :
                    domain.append(('date','>=',kw['start']))

            if 'end' in kw:
                if kw['end'] and kw['end'] != 'False' :
                    domain.append(('date','<=',kw['end']))

            if sale:
                domain.append(('order_id','=',order.id))
                schedule_dues = self.env['schedule.dues.land'].search(domain)
                self.get_report_xls_data_sale(workbook, sheet,sale,schedule_dues)
            else:
                domain += [('order_id.company_id','=',company.id)]
                #,('type_schedule','=','dues')
                schedule_dues = self.env['schedule.dues.land'].search(domain)
                #self.get_report_xls_data(workbook, sheet,company,schedule_dues)
                self.get_report_xls_data_optimizado(workbook, sheet,company,schedule_dues)




        workbook.close()
        excel_file = base64.encodebytes(fp.getvalue())
        fp.close()
        return excel_file

    def get_report_xls_data_year(self,workbook, sheet,orders,year):
        xc = 1
        bold = workbook.add_format({'bold': True , 'align': 'center', 'valign': 'vcenter' })
        format_body = workbook.add_format({
            'bold': False, 'align': 'center', 'valign': 'vcenter',
            'bottom': 2, 'top': 2, 'left': 2, 'right': 2}
        )

        bg_azul_text_white = workbook.add_format({
            'bg_color': '#003366', 'border': 1 , 'bold': True ,
            'align': 'center', 'valign': 'vcenter' , 'color': 'white'
        })

        # Definir el formato para el fondo verde claro
        green_format = workbook.add_format({'bg_color': '#90EE90', 'border': 1})
        # Definir el formato para el fondo rojo claro
        red_format = workbook.add_format({'bg_color': '#FFCCCB', 'border': 1})
        gray_format = workbook.add_format({'bg_color': '#A9A9A9', 'border': 1 , 'align': 'center', 'valign': 'vcenter'})


        sheet.write(xc, 1, 'EXPEDIENTE', bg_azul_text_white)
        sheet.set_column('B:B', 20)

        sheet.write(xc, 2, 'MZ', bg_azul_text_white)
        sheet.write(xc, 3, 'LOTE', bg_azul_text_white)
        sheet.set_column('C:D', 10)


        sheet.write(xc, 4, 'NOMBRE DE CLIENTE', bg_azul_text_white)
        sheet.set_column('E:E', 50)

        sheet.write(xc, 5, 'ESTADO', bg_azul_text_white)
        sheet.set_column('F:F', 20)

        sheet.write(xc, 6, 'ESTADO PAGO', bg_azul_text_white)
        sheet.set_column('G:G', 20)

        sheet.write(xc, 7, 'MESES A PAGAR', bg_azul_text_white)
        sheet.set_column('H:H', 15)

        sheet.write(xc, 8, 'MESES PAGADOS', bg_azul_text_white)
        sheet.set_column('I:I', 15)

        sheet.write(xc, 9, 'CUOTA', bg_azul_text_white)
        sheet.set_column('J:J', 15)

        n_start = 10

        sheet.write(xc, n_start, 'CREDITO ANUAL', bg_azul_text_white)


        meses = ["Enero","Febrero","Marzo", "Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        c = 0
        for mes in meses:
            c += 1
            sheet.write(xc, n_start + c, mes, bg_azul_text_white)

        sheet.set_column('K:W', 15)

        sheet.write(xc, n_start + 13, 'APORTADO', bg_azul_text_white)
        sheet.write(xc, n_start + 14, 'SALDO', bg_azul_text_white)





        xc += 1

        for order in orders:

            schedule_land_dues = order.get_schedule_x_year(year)

            if not schedule_land_dues:
                continue

            format_bodyx = gray_format if order.stage_land == 'cancel' else format_body

            sheet.write(xc, 1, order.nro_internal_land, format_bodyx)
            sheet.write(xc, 2, order.mz_land, format_bodyx)
            sheet.write(xc, 3, order.lot_land, format_bodyx)
            sheet.write(xc, 4, order.partner_id.display_name, format_bodyx)
            sheet.write(xc, 5, stage_land.get(order.stage_land) if order.stage_land else '', format_bodyx)
            sheet.write(xc, 6, stage_payment_lan.get(order.stage_payment_lan) if order.stage_payment_lan else '', format_bodyx)

            #7 MESES A PAGAR
            m_a_pgar = 0
            #8 MESES PAGADOS
            m_pgados = 0
            #9 CUOTA
            sheet.write(xc, 9,  order.value_due_land, format_bodyx)
            #10 CREDITO ANUAL

            ##CUOTAS




            pagado = 0
            for sche in schedule_land_dues:
                sh_month = sche.date.month

                if sche.amount_due_land > 0 :
                    pagadox = sche.amount_due_land + sche.get_value_adelantos()
                    pagado += pagadox
                    sheet.write(xc, n_start + sh_month, pagadox, green_format)
                    m_pgados += 1
                else:
                    sheet.write(xc, n_start + sh_month, sche.amount , red_format)
                m_a_pgar += 1

            #7 MESES A PAGAR
            sheet.write(xc, 7, m_a_pgar, format_bodyx)
            #8 MESES PAGADOS
            sheet.write(xc, 8, m_pgados, format_bodyx)
            #9 CREDITO ANUAL
            credito = m_a_pgar * order.value_due_land
            sheet.write(xc, 10, credito, format_bodyx)

            sheet.write(xc, n_start + 13, pagado, format_bodyx)
            sheet.write(xc, n_start + 14, credito - pagado, format_bodyx)
            sheet.set_column('X:Y', 20)


            xc += 1


    def get_report_xls_data_sale(self,workbook, sheet,order,schedule_dues):



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
            'bg_color': '#ADD8E6', 'border': 1 , 'bold': True
        })
        bg_azulwhite = workbook.add_format({
            'bg_color': '#ADD8E6', 'border': 1
        })

        #sheet.write(xc, 1, 'REPORTE  CUOTAS', bold)
        sheet.merge_range('B1:G1', 'REPORTE CUOTAS', bg_azul_text_white)


        sheet.write(xc, 1, 'CLIENTE:', bg_azulwhite_bold)
        sheet.merge_range('C2:G2', order.partner_id.display_name, bg_azulwhite)
        xc += 1

        sheet.write(xc, 1, 'MZ-LT:', bg_azulwhite_bold)
        sheet.merge_range('C3:G3', order.mz_lot, bg_azulwhite)
        xc += 1

        sheet.write(xc, 1, 'DEVOLUCION:', bg_azulwhite_bold)
        sheet.merge_range('C4:G4', order.percentage_refund_land, bg_azulwhite)
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



    def get_report_xls_data(self,workbook, sheet,company,schedule_dues):




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




        #raise ValueError(len(schedule_dues))

        for schedule_due in schedule_dues:

            order = schedule_due.order_id

            invoice_pagada = schedule_due.invoice_date if schedule_due.invoice_date else fields.Datetime.now().date()

            sheet.write(xc, 1, schedule_due.order_id.nro_internal_land, format_body)
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



    def get_report_xls_data_optimizado(self, workbook, sheet, company, schedule_dues):
        xc = 1
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        format_body = workbook.add_format({'bold': False, 'align': 'center', 'valign': 'vcenter', 'bottom': 2, 'top': 2, 'left': 2, 'right': 2})
        format_red = workbook.add_format({'bg_color': '#FFCCCC', 'font_color': '#000000', 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        bg_azul_text_white = workbook.add_format({
            'bg_color': '#003366', 'border': 1 , 'bold': True ,
            'align': 'center', 'valign': 'vcenter' , 'color': 'white'
        })
        green_format = workbook.add_format({'bg_color': '#90EE90', 'border': 1 , 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        gray_format  = workbook.add_format({'bg_color': '#A9A9A9', 'border': 1 , 'bold': True, 'align': 'center', 'valign': 'vcenter'})

        headers = ['EXPEDIENTE', 'MZ', 'LOTE', 'NOMBRE DE CLIENTE', 'METRAJE', 'FECHA DE COBRANZA', 'FECHA PAGADA / HOY',
                   'DIAS VENCIDOS', 'DESCRIPCION', 'MONTO', 'ETAPA', 'PROVEEDOR' ,'EMPRESA', 'COMPROBANTE DE CUOTA', 'FECHA DE EMISION', 'ESTADO']
        sheet.write_row(xc, 1, headers, bg_azul_text_white)

        # Ajustar columnas
        sheet.set_column('B:B', 10)
        sheet.set_column('C:D', 10)
        sheet.set_column('E:E', 50)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:H', 20)
        sheet.set_column('I:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 50)
        sheet.set_column('O:O', 25)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 15)

        xc += 1

        data_to_write = []

        for schedule_due in schedule_dues:
            order = schedule_due.order_id
            invoice_pagada = schedule_due.invoice_date if schedule_due.invoice_date else fields.Datetime.now().date()
            dias_vencidos = (invoice_pagada - schedule_due.date).days if schedule_due.date else 0

            if dias_vencidos < 0 :
                dias_vencidos = 0



            descripcion = ''

            if schedule_due.type_schedule == 'dues':
                descripcion = f"CUOTA N° {schedule_due.number_due}"

            if schedule_due.type_schedule == 'initial':
                descripcion = "INICIAL"

            if schedule_due.type_schedule == 'advances':
                descripcion = f"ADELANTO CUOTA{schedule_due.number_due}"

            if schedule_due.type_schedule == 'independence':
                descripcion = "Independizacion"


            row_data = [
                schedule_due.order_id.nro_internal_land,
                order.mz_land,
                order.lot_land,
                order.partner_id.display_name,
                order.m2_land,
                str(schedule_due.date),
                str(invoice_pagada),
                dias_vencidos,
                descripcion ,
                #schedule_due.number_due, #DESCRIPCION
                schedule_due.amount_due_land,
                order.sector_land,
                order.seller_land_id.display_name or '' ,
                order.company_id.display_name,
                schedule_due.move_id.display_name if schedule_due.move_id else  '',
                str(schedule_due.invoice_date or ''),
                'CANCELADO' if schedule_due.is_paid else 'PENDIENTE'
            ]

            data_to_write.append(row_data)

            # Escribir la fila de datos
            sheet.write_row(xc, 1, row_data, format_body)

            # Aplicar formato al estado
            if schedule_due.is_paid:
                sheet.write(xc, 15, 'PAGADO', green_format)
            else:

                #si ya la venta esta cancelada / resolucion
                if order.stage_land == 'cancel' :
                    sheet.write(xc, 15, 'RESOLUCION', gray_format)
                else:
                    sheet.write(xc, 15, 'PENDIENTE', format_red)

            xc += 1

