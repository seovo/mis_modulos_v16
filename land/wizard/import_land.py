from odoo import api, fields, models
import subprocess
import sys

from datetime import date, datetime, time

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import base64
except:
    install('base64')

try:
    import openpyxl
except:
    install('openpyxl')

try:
    import pandas
except:
    install('pandas')


import pandas as pd
import base64

import io

class ImportCiHrAttendance(models.TransientModel):
    _name = "import.land"
    file = fields.Binary(string="Archivo")
    file_name = fields.Char()

    def import_excell(self):
        for sale in self.env['sale.order'].search([
            ('price_total_land','!=',False),
            ('price_total_land','!=',0),
            ('state','=','draft')
        ]):
            sale.action_confirm()

    def import_excell_sales(self):


        #wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        #hoja = wb.sheet_by_name('CVENTAS')

        archivo_decodificado = base64.decodebytes(self.file)
        # Crear un objeto BytesIO a partir del archivo decodificado
        archivo_io = io.BytesIO(archivo_decodificado)

        # Leer el archivo Excel con Pandas
        ventas = pd.read_excel(archivo_io)

        #raise ValueError(str(df))

        c = 0

        for index, row in ventas.iterrows():


            c += 1

            if c > 700 :
                break

            try:
                expediente = str(int(row['EXP']))
            except:
                break
                raise ValueError([c, str(row['EXP'])])

            if c == 231:
                expediente = '231'


            if c == 397:
                expediente = '397'






            order = self.env['sale.order'].search([('nro_internal_land','=',str(expediente))])
            #if c == 231 :
            #    raise ValueError(order)
            if not order :


                # raise ValueError(row)
                user_id = self.env['res.users'].search([('name', '=', row['ASESOR']),'|',('active','=',True),('active','=',False)])
                if not user_id:
                    user_id = self.env['res.users'].search([('name', 'ilike', row['ASESOR']),'|',('active','=',True),('active','=',False)])
                    if not user_id:
                        raise ValueError(row['ASESOR'])
                mz_lote = str(row['LT'])
                etapa = str(row['ETAPA'])
                SECTOR = str(row['SECTOR'])

                cliente = row[' CLIENTE (PERSONA JURIDICA - NATURAL)']

                tipo_doc = str(row['ID']).replace(' ', '').replace('*', '')
                ident_type = self.env.ref('l10n_pe.it_DNI')
                try:
                    tipo_doc = int(tipo_doc)
                    tipo_doc = str(str(tipo_doc).zfill(8))
                except:
                    if tipo_doc.find('CE') != -1:
                        tipo_doc = tipo_doc.replace('CE', '')
                        ident_type = self.env.ref('l10n_latam_base.it_fid')
                    else:
                        if tipo_doc.find('CPP') != -1:
                            tipo_doc = tipo_doc.replace('CPP', '')
                            ident_type = self.env.ref('l10n_pe.it_CPP')
                        else:
                            if tipo_doc[0] == 0 or tipo_doc[0] == '0' or tipo_doc[0] == 'O':

                                tipo_doc = tipo_doc.replace('O', '0')

                                tipo_doc = str(str(tipo_doc).zfill(8))
                                ident_type = self.env.ref('l10n_latam_base.it_fid')
                            else:
                                if tipo_doc.find('PAS') != -1:
                                    tipo_doc = tipo_doc.replace('PAS', '')
                                    ident_type = self.env.ref('l10n_latam_base.it_pass')
                                else:
                                    if tipo_doc == 'nan':
                                        pass
                                    else:
                                        raise ValueError(str(tipo_doc))

                email = row['EMAIL']
                whatsap = row['WHATSAPP']
                M2 = row['M2']
                T_CUOTAS = int(row['T CUOTAS'])
                VALOR_CUOTA = float(row['VALOR CUOTA'])

                FECHA_PRIMERA_CUOTA = row['FECHA PRIMERA CUOTA']

                ESTADO = row['ESTADO']

                CRONO = row['CRONO']
                try:
                    GRACIA = int(row['GRACIA'])
                except:
                    GRACIA = 0
                try:
                    MORA = float(row['MORA'])
                    if str(MORA) == 'nan':
                        MORA = 0
                except:
                    MORA = 0

                # if expediente == '97':
                #    raise ValueError(str(MORA),type(MORA))

                percentage_refund_land = 0
                DEVOLUCION = str(row['% DEVOLUCION'])
                if DEVOLUCION.find('50'):
                    percentage_refund_land = 50

                MODALIDAD = str(row['MODALIDAD'])

                modality_land = None
                if MODALIDAD.find('SOLTER') != -1:
                    modality_land = 'single'
                if MODALIDAD.find('BAJA') != -1:
                    modality_land = 'low_customer'

                if MODALIDAD.find('COF') != -1:
                    modality_land = 'confirmer'

                if MODALIDAD.find('DIVOR') != -1:
                    modality_land = 'divorcee'

                if MODALIDAD.find('VIUDA') != -1:
                    modality_land = 'divorcee'

                if MODALIDAD.find('TRAN') != -1:
                    modality_land = 'transfer'

                obs_modality_land = MODALIDAD

                FECHA_FIRMA = row[18]

                WHATSAPP = str(row[24])
                obs_modality_land += '\n' + WHATSAPP

                OBS = str(row['OBS'])
                obs_modality_land += '\n' + OBS

                partner_id = self.env['res.partner'].search([('vat', '=', str(tipo_doc))])
                if not partner_id:
                    partner_id = self.env['res.partner'].create({
                        'name': str(cliente),
                        'vat': tipo_doc,
                        'l10n_latam_identification_type_id': ident_type.id,
                        'street': SECTOR,
                        'email': email,
                        'mobile': whatsap,

                    })



                FECHA_FIRMA = FECHA_FIRMA.date()
                try:
                    FECHA_PRIMERA_CUOTA = FECHA_PRIMERA_CUOTA.date()
                except:
                    obs_modality_land += '\n' + str(FECHA_PRIMERA_CUOTA)
                    FECHA_PRIMERA_CUOTA = None



                # raise ValueError(FECHA_PRIMERA_CUOTA,type(FECHA_PRIMERA_CUOTA))
                data_order = {
                    'name': 'S'+str(expediente).zfill(5),
                    'nro_internal_land': str(expediente),
                    'user_id': user_id.id,
                    'partner_id': partner_id.id,
                    'mz_lot': mz_lote,
                    'sector': etapa,
                    'date_sign_land': FECHA_FIRMA,
                    'date_first_due_land': FECHA_PRIMERA_CUOTA,
                    'crono_land': CRONO,
                    'days_tolerance_land': GRACIA,
                    'value_mora_land': MORA,
                    'percentage_refund_land': percentage_refund_land,

                    'm2_land': M2,
                    'dues_land': T_CUOTAS,
                    'value_due_land': VALOR_CUOTA,
                    'modality_land': modality_land,
                    'obs_modality_land': obs_modality_land,

                }

                try:
                    if ESTADO.find('FIRM') != -1:
                        data_order.update({
                            'stage_land': 'signed'
                        })
                    else:
                        raise ValueError(str(ESTADO))
                except:
                    raise ValueError(str(ESTADO))

                order = self.env['sale.order'].create(data_order)




                hora_desejada = time(9, 30)  # Hora:Minuto (9:30)

                if not order:
                    raise ValueError(c)

                data_hora_desejada = datetime.combine(order.date_sign_land, hora_desejada)
                order.date_order = data_hora_desejada
            #else:
            #    order.name = 'S'+str(expediente).zfill(5)

            '''
            else:
                precio_total = float(row['PRECIO TOTAL'])
                credito = float(row['CREDITO'])
                INICIAL = float(row['INICIAL'])
                T_CUOTAS = int(row['T CUOTAS'])

                if str(precio_total) == 'nan':
                    precio_total = 0

                if str(credito) == 'nan':
                    credito = 0


                if str(INICIAL) == 'nan':
                    INICIAL = 0


                if str(T_CUOTAS) == 'nan':
                    T_CUOTAS = 0

                order.update({
                    'price_total_land': precio_total,
                    'price_initial_land': INICIAL,
                    'price_credit_land': credito,
                    'dues_land': T_CUOTAS,
                })
            '''

            if not order.order_line:
                precio_total = float(row['PRECIO TOTAL'])
                credito = float(row['CREDITO'])
                INICIAL = float(row['INICIAL'])
                T_CUOTAS = int(row['T CUOTAS'])

                if str(precio_total) == 'nan':
                    precio_total = 0

                if str(credito) == 'nan':
                    credito = 0

                if str(INICIAL) == 'nan':
                    INICIAL = 0

                if str(T_CUOTAS) == 'nan':
                    T_CUOTAS = 0

                price_unit = ( credito ) / order.dues_land

                order.update({
                    'price_total_land'   : precio_total ,
                    'price_initial_land' : INICIAL ,
                    'price_credit_land'  : credito ,
                    'dues_land': T_CUOTAS,
                })

                product_inicial = self.env['product.product'].search([('name', 'ilike', 'INICIAL')])

                order.order_line += self.env['sale.order.line'].new({
                    'product_id': product_inicial.id ,
                    'name': product_inicial.display_name ,
                    'product_uom_qty': 1,
                    'price_unit': INICIAL ,
                    'tax_id': [(6, 0, [self.env.ref('l10n_pe.1_sale_tax_exo').id])]
                })

                product_total = self.env['product.product'].search([('name','ilike','TERRENO')])



                order.order_line += self.env['sale.order.line'].new({
                    'product_id': product_total.id ,
                    'name': product_total.display_name ,
                    'product_uom_qty': T_CUOTAS ,
                    'price_unit': price_unit ,
                    'tax_id': [(6,0,[self.env.ref('l10n_pe.1_sale_tax_exo').id])]
                })
            #else:
            #    for line in order.order_line:
            #        line.tax_id = [(6,0,[self.env.ref('l10n_pe.1_sale_tax_exo').id])]




        #for i in range(hoja.nrows):
        #    if i >= 1:
        #        pass