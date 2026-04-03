from odoo import api, fields, models
from odoo.exceptions import UserError

import requests
# URL del servicio SOAP
url = 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php'
import hashlib
import subprocess

from datetime import datetime, timedelta
import pytz

import http.client
import json
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import xmltodict
except:
    install('xmltodict')



class AccountMove(models.Model):
    _inherit = "account.move"
    log_smc = fields.Text()

    type_negocio_area_smc = fields.Selection([
        ('Armadora', 'Armadora'),
        ('Maquiladora', 'Maquiladora')
    ], string="Tipo Negocio",related='partner_id.type_negocio_area_smc',readonly=False)
    area_empresarial_smc = fields.Many2one('area.empresarial.smc', string="Area Empresarial",
                                           related='partner_id.area_empresarial_smc',readonly=False)
    clave_colonia_smc = fields.Many2one('catalogos.colonias',string='Colonia',
                                        related='partner_id.clave_colonia_smc',readonly=False)
    smc_model_ids = fields.One2many('smc.model','move_id')
    state_smc = fields.Selection([('draft', 'Pendiente'), ('error', 'Error'), ('sent', 'Enviado')],string='Estado SMC')

    def action_post(self):

        if len(self) == 1:

            if self.company_id.smc_category_ids and self.company_id.smc_active:
                exist_categ_smc = False

                for line in self.line_ids:
                    if line.product_id:
                        if line.product_id.categ_id in self.company_id.smc_category_ids:
                            exist_categ_smc = True

                incomplete_datos = False

                if not self.clave_colonia_smc:
                    incomplete_datos = True

                if not self.area_empresarial_smc:
                    incomplete_datos = True

                if not self.type_negocio_area_smc:
                    incomplete_datos = True

                if incomplete_datos:
                    view = self.env.ref('smc_connector_jz.view_move_form_smc')
                    return {
                        "name": f"COMPLETAR DATOS :   {self.partner_id.display_name}",
                        "type": "ir.actions.act_window",
                        "view_mode": "form",
                        "res_model": "account.move",
                        "target": "new",
                        "res_id": self.id,
                        "view_id": view.id
                    }









        res = super().action_post()

        return res

    def generar_token(self,numero_dt):

        timezone = pytz.timezone('America/Mexico_City')
        # Establecer la zona horaria

        ahora = datetime.now(timezone)


        una_hora_menos = ahora - timedelta(hours=1)


        #raise ValueError(una_hora_menos)
        #raise ValueError(fields.datetime.now())
        # Formatear la fecha y hora como 'YYYYMMDDHH'
        fecha_formateada = una_hora_menos.strftime('%Y%m%d%H')



        # Concatenar el número de DT con la fecha formateada
        dato_previo = f"{numero_dt}{fecha_formateada}"

        # Crear el hash MD5 del dato previo
        token = hashlib.md5(dato_previo.encode()).hexdigest()

        return token


    def send_smc_data(self):

        if len(self) == 1:

            if not self.company_id.smc_active:
                return

            if self.journal_id not in self.company_id.smc_journal_ids:
                return

            if self.company_id.smc_date_after:
                if self.invoice_date < self.company_id.smc_date_after:
                    return

            if self.partner_id in self.company_id.smc_excluded_partner_ids:
                return

            incomplete_datos = False

            if not self.clave_colonia_smc:
                incomplete_datos = True

            if not self.area_empresarial_smc:
                incomplete_datos = True

            if not self.type_negocio_area_smc:
                incomplete_datos = True

            if incomplete_datos:
                view = self.env.ref('smc_connector_jz.view_move_form_smc')
                return {
                    "name": f"COMPLETAR DATOS :   {self.partner_id.display_name}",
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": "account.move",
                    "target": "new",
                    "res_id": self.id,
                    "view_id": view.id
                }


        if not self.env.company.smc_active:
            return

        invoices = ''

        for record in self:

            dt = record.send_smc_data_one()

            if dt:
                invoices += dt



        if invoices == '':
            if len(self) == 1:
                raise UserError('NO SE ENCONTRO LINEAS DE VENTA')
            return

        # Ejemplo de uso
        numero_dt = self.env.company.smc_dt # '43006'
        smc_usuario = self.env.company.smc_usuario #alfen_t
        smc_password = self.env.company.smc_password #PwSnil91p_Pb7q9Z
        smc_name_dt = self.env.company.smc_name_dt #SERVICIOS INDUSTRIALES ALFEN

        token_generado = self.generar_token(numero_dt)
        #print(f"Token generado: {token_generado}")

        # Establecer los headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            #'Content-Type': 'text/xml',
            'SOAPAction': 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php#enviarDetalleVenta'
        }



        soap_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php">
    <soap:Body>
        <tns:enviarDetalleVenta>
            <usuario>{smc_usuario}</usuario>
            <password>{smc_password}</password>
            <token>{token_generado}</token>
            <numeroDT>{numero_dt}</numeroDT>
            <nombreDT>{smc_name_dt}</nombreDT>
            <oListaClientes>
                {invoices}
            </oListaClientes>
        </tns:enviarDetalleVenta>
    </soap:Body>
</soap:Envelope>'''

        #raise ValueError(soap_body)

        soap_body = soap_body.encode('utf-8')

        #RESPUESTA
        response = requests.post(url, data=soap_body, headers=headers)
        xml_data = response.text
        xml_dict = xmltodict.parse(xml_data)
        json_responsex = str(json.dumps(xml_dict, indent=4))
        #.encode('utf-8')

        xml_dict_send = xmltodict.parse(soap_body)
        xml_send_smc = str(json.dumps(xml_dict_send, indent=4))
        self.xml_send_smc = xml_send_smc

        # Extraer los valores que necesitas
        try:
            resultado = xml_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:enviarDetalleVentaResponse'][
                'enviarDetalleVentaResult']
        except:
            mensajes = str(json_responsex)

            self.log_smc = mensajes
            st_smc = 'error'
            self.state_smc = st_smc


            return


        numero_registros_recibidos = resultado['numeroRegistrosRecibidos']['#text']
        numero_registros_agregados = resultado['numeroRegistrosAgregados']['#text']
        try:
            mensajes = resultado['mensajes']['item']['#text']
        except:
            mensajes = str(resultado)





            # Imprimir los resultados
        msg = f'''
              Número de registros recibidos : {numero_registros_recibidos}
              Número de registros agregados: {numero_registros_agregados}
              Mensajes: {mensajes}
        '''

        self.log_smc = mensajes





        if self.smc_model_ids:


            smc_model = self.smc_model_ids[0]

            smc_model.xml_sent = xml_send_smc
            smc_model.log_smc = json_responsex
            smc_model.msg = msg

            if int(numero_registros_recibidos) > 0 :
                st_smc = ''
                if int(numero_registros_agregados) != int(numero_registros_recibidos):
                    st_smc = 'error'

                else:
                    st_smc = 'sent'

                smc_model.state = st_smc
                self.state_smc = st_smc


    def send_smc_data_one(self):

        dx = {
            # 'cliente':

        }




        lines_availables = []

        if self.journal_id not in self.company_id.smc_journal_ids:
            return

        if self.company_id.smc_date_after:
            if self.invoice_date < self.company_id.smc_date_after:
                return

        if self.partner_id in self.company_id.smc_excluded_partner_ids:
            return



        for line in self.line_ids:
            if line.product_id.categ_id in  self.company_id.smc_category_ids:
                lines_availables.append(line)

        if not lines_availables:
            return ''



        lines = ''

        colony = self.clave_colonia_smc.descripcion


        if not colony:
            raise UserError('Indique una colonia')

        area_smc = self.partner_id.type_negocio_area_smc

        if not area_smc:
            raise UserError('INDIQUE EL TIPO DE NEGOCIO AL CLIENTE')

        if not self.partner_id.area_empresarial_smc:
            raise UserError('NO EXISTE AREA EMPRESARIAL')

        areaempresarial = self.partner_id.area_empresarial_smc.name




        #FLETE = PRECIO VENTA - PRECIO LISTA
        flete = 0

        add_lines = []


        for line_av in lines_availables:

            name_product = line_av.product_id.name
            code_japon = line_av.product_id.default_code

            if code_japon:
                code_japon = code_japon.replace(' ','')

            if name_product:
                name_product = name_product.replace(' ','')



            #if not code_japon or code_japon == '':
            #    raise UserError(f'''INDIQUE CODIGO JAPON PARA {name_product}''')

            #if code_japon:
            #    if len(code_japon) < 6 :
            #        raise  UserError(f'''El codigo de referencia no debe ser menor a 6 digitos , {code_japon} , producto {name_product}''')

            #    first_code_japon = code_japon[0]

            #    if str(first_code_japon) in ['0','1','2','3','4','5','6','7','8','9']:
            #        raise UserError(f'''El codigo japon no puede comenzar con un numero {code_japon} , en el producto {name_product}''')

            lines += f'''
            <item>
               <banderaFleteIncluidoEnPrecio>false</banderaFleteIncluidoEnPrecio>
               <codigoInterno>{name_product}</codigoInterno>
               <codigoJapon>{code_japon}</codigoJapon>
               <cantidad>{int(line_av.quantity)}</cantidad>
               
               <precioLista>{line_av.product_id.standard_price}</precioLista>
               <precioVenta>{line_av.price_unit}</precioVenta>
               <montoUnitarioFlete>{flete}</montoUnitarioFlete>
               <descuentoPorPartida>0</descuentoPorPartida>
               <lineaFactura>{int(line_av.sequence)}</lineaFactura>
            </item>
            '''

            add_lines.append({
                'codigo_interno': name_product ,
                'codigo_japon': code_japon ,
                'cantidad': int(line_av.quantity) ,
                'precio_lista': line_av.product_id.standard_price ,
                'precio_venta': line_av.price_unit ,
                'monto_unitario_flete': flete ,
                'linea_factura': int(line_av.sequence)
            })
            #<ordenCompra></ordenCompra>
            #<codigoProductoDT>{line_av.product_id.default_code}</codigoProductoDT>


        if not self.folio_fiscal:
            raise UserError('No se Indico Folio Fiscal')

        texto = self.name

        # Extraer el primer número como serie
        serie = texto[0]  # El primer carácter después de 'F'

        # Extraer el resto como folio
        folio = texto[1:]  # Desde el primer carácter hasta el final

        # Imprimir resultados
        #print(f"Serie: {serie}")
        #print(f"Folio: {folio}")

        moneda = None
        tipo_cambio = 1

        if self.currency_id == self.env.ref('base.MXN'):
            moneda = "MXN"

        if self.currency_id == self.env.ref('base.USD'):
            moneda = "USD"
            tipo_cambio = self.inv_exchange_rate_display

        tipo_combrobante = None

        if self.type == 'out_invoice':
            tipo_combrobante = 'I'

        if self.type == 'out_refund':
            tipo_combrobante = 'E'

        subtotal = self.amount_untaxed
        iva = self.amount_total-self.amount_untaxed
        total = self.amount_total

        item = f'''
        <item>
            
            <clienteFinal>{self.partner_id.id}</clienteFinal>
            <RFC>{self.partner_id.vat}</RFC>
            <razonSocial>{self.partner_id.name}</razonSocial>
            <codigoPostal>{self.clave_colonia_smc.c_codigopostal}</codigoPostal>
            <colonia>{colony}</colonia>
            <calle>{self.partner_id.street_name}</calle>
            <numeroExterior>{self.partner_id.street_number}</numeroExterior>
            <tipoNegocioArea>{area_smc}</tipoNegocioArea>
            <areaEmpresarial>{areaempresarial}</areaEmpresarial>
            <oListaFacturas>
                <item>
                    <UUID>{self.folio_fiscal}</UUID>
                    <folioFactura>{folio}</folioFactura>
                    <serie>{serie}</serie>
                    <fechaFactura>{str(self.date)}</fechaFactura>
                    <tipoComprobante>{tipo_combrobante}</tipoComprobante>
                    <moneda>{moneda}</moneda>
                    <tipoCambio>{tipo_cambio}</tipoCambio>
                    <subtotal>{subtotal}</subtotal>
                    <descuento>0</descuento>
                    <IVA>{iva}</IVA>
                    <total>{total}</total>
                    <oListaItems>
                    {lines}
                    </oListaItems>
                </item>
                
            </oListaFacturas>
        </item>
        '''
        #motivoDescuento

        dx.update({
            'cliente': str(self.partner_id.id),
            'rfc': str(self.partner_id.vat)   ,
            'razon_social': self.partner_id.name ,
            'codigo_postal': self.partner_id.zip ,
            'colonia': colony ,
            'calle': self.partner_id.street_name ,
            'numero_exterior': self.partner_id.street_number ,
            'tipo_negocio_area': area_smc ,
            'area_empresarial': areaempresarial ,
            'uuid': self.folio_fiscal ,
            'serie': serie ,
            'folio_factura': folio,
            'fecha_factura': self.date ,
            'tipo_comprobante': tipo_combrobante ,
            'moneda': moneda ,
            'tipoCambio': tipo_cambio ,
            'subtotal': subtotal ,
            'iva': iva ,
            'total': total


        })


        if not self.smc_model_ids:
            self.smc_model_ids += self.env['smc.model'].new(dx)
        else:
            self.smc_model_ids[0].write(dx)

        if self.smc_model_ids[0].line_ids:
            self.smc_model_ids[0].line_ids.unlink()

        if add_lines:
            for dxx in add_lines:
                self.smc_model_ids[0].line_ids += self.env['smc.model.item'].new(dxx)


        return item


    def send_masive_smc(self):
        for record in self:
            record.send_smc_data()


    def send_masive_smc_cron(self):
        companys = self.env['res.company'].search([('smc_active','=',True)])

        for company in companys:
            moves =  company.action_view_moves_smc(retornar=True)

            moves = moves[:5]

            for move in moves:
                try:
                    move.send_masive_smc()
                except:
                    continue

    def send_alert_smc_cron(self):
        companys = self.env['res.company'].search([('smc_active', '=', True)])

        bot_user = self.env.ref('base.user_root')  # o búsqueda de usuario bot
        bot_partner_id = bot_user.partner_id.id if bot_user else False
        author_partner_id = bot_partner_id

        for company in companys:
            if company.smc_channel_id:


                channel = company.smc_channel_id

                if not channel.channel_last_seen_partner_ids:
                    continue

                partner_ids = []

                for cpartner in channel.channel_last_seen_partner_ids:
                    partner_ids.append(cpartner.partner_id.id)

                #raise ValueError(channel)

                #buscar facturas que faltan completar datos

                domain_add = [
                    #('state_smc', '=', False),
                    ('partner_id.type_negocio_area_smc', '=', False),
                    ('partner_id.area_empresarial_smc', '=', False),
                    ('partner_id.clave_colonia_smc', '=', False)
                ]
                moves = company.action_view_moves_smc(retornar=True,domain_add=domain_add)
                if moves:
                    moves_names = []
                    for mv in moves:
                        moves_names.append(mv.name)

                    body = f'Las siguientes facturas tienen incompleto sus datos {" , ".join(moves_names)} en la compañia {company.name}'
                    body = f'''
                                    <div class="alert alert-dark" role="alert">
                                      <p><b>compañia {company.name}</b></p>
                                      Las siguientes facturas fueron enviados con error {" , ".join(moves_names)}
                                    </div>
                                    '''
                    subject = 'FACTURAS INCOMPLETAS SMC'

                    # raise ValueError(author_partner_id)

                    wizard = self.env['mail.compose.message'].create({
                        'partner_ids': partner_ids,
                        'body': body,
                        'subject': subject,
                        'model': 'mail.channel',
                        'res_id': channel.id,
                        'author_id': author_partner_id,
                        'message_type': 'comment'
                    })

                    wizard.action_send_mail()


                #ENVIAR LAS FACTURAS CON ERROR

                domain_add = [
                    ('state_smc', '=', 'error')
                ]
                moves = company.action_view_moves_smc(retornar=True, domain_add=domain_add)

                if moves:
                    moves_names = []
                    for mv in moves:
                        moves_names.append(mv.name)

                    body = f'''
                                    <div class="alert alert-danger" role="alert">
                                      <p><b>compañia {company.name}</b></p>
                                      Las siguientes facturas fueron enviados con error {" , ".join(moves_names)}
                                    </div>
                                    '''
                    subject = 'FACTURAS CON ERROR SMC'

                    # raise ValueError(author_partner_id)

                    wizard = self.env['mail.compose.message'].create({
                        'partner_ids': partner_ids,
                        'body': body,
                        'subject': subject,
                        'model': 'mail.channel',
                        'res_id': channel.id,
                        'author_id': author_partner_id,
                        'message_type': 'comment'
                    })

                    wizard.action_send_mail()













