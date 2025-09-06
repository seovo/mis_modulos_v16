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
    xml_send_smc = fields.Text()

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

        invoices = ''

        for record in self:
            invoices += record.send_smc_data_one()

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


        response = requests.post(url, data=soap_body.encode('utf-8'), headers=headers)
        xml_data = response.text
        # Mostrar la respuesta

        xml_dict = xmltodict.parse(xml_data)
        json_responsex = str(json.dumps(xml_dict, indent=4))

        record.log_smc = json_responsex


        xml_dict_send = xmltodict.parse(soap_body.encode('utf-8'))
        record.xml_send_smc = str(json.dumps(xml_dict_send, indent=4))





        #raise ValueError(response.text)
        #print(response.text)




    def send_smc_data_one(self):

        lines_availables = []

        if self.partner_id is self.company_id.smc_excluded_partner_ids:
            return

        for line in self.line_ids:
            if line.product_id.categ_id in  self.company_id.smc_category_ids:
                lines_availables.append(line)

        if not lines_availables:
            return



        lines = ''
        colony = ''

        try:
            colony = self.partner_id.colony
        except:
            colony = self.x_colonia

        area_smc = self.partner_id.type_negocio_area_smc

        if not area_smc:
            raise UserError('INDIQUE EL TIPO DE NEGOCIO AL CLIENTE')

        areaempresarial = self.partner_id.area_empresarial_smc

        if not areaempresarial:
            raise UserError('NO EXISTE AREA EMPRESARIAL')


        for line_av in lines_availables:
            lines += f'''
            <item>
               <banderaFleteIncluidoEnPrecio>false</banderaFleteIncluidoEnPrecio>
               <codigoInterno>{line_av.product_id.name}</codigoInterno>
               <codigoJapon>{line_av.product_id.default_code}</codigoJapon>
               <cantidad>{int(line_av.quantity)}</cantidad>
               
               <precioLista>{line_av.product_id.standard_price}</precioLista>
               <precioVenta>{line_av.price_subtotal}</precioVenta>
               <montoUnitarioFlete>{line_av.price_unit}</montoUnitarioFlete>
               <descuentoPorPartida>0</descuentoPorPartida>
               <lineaFactura>{int(line_av.id)}</lineaFactura>
            </item>
            '''
            #<ordenCompra></ordenCompra>
            #<codigoProductoDT>{line_av.product_id.default_code}</codigoProductoDT>

        try:
            folio =  self.folio_fiscal
        except:
            folio = '85114ba1-aa08-43f2-b8d4-e6ae87f5b513'

        serie = 'F'


        item = f'''
        <item>
            
            <clienteFinal>{self.partner_id.id}</clienteFinal>
            <RFC>{self.partner_id.vat}</RFC>
            <razonSocial>{self.partner_id.name}</razonSocial>
            <codigoPostal>{self.partner_id.zip}</codigoPostal>
            <colonia>{colony}</colonia>
            <calle>{self.partner_id.street_name}</calle>
            <numeroExterior>{self.partner_id.street_number}</numeroExterior>
            <tipoNegocioArea>{area_smc}</tipoNegocioArea>
            <areaEmpresarial>{areaempresarial}</areaEmpresarial>
            <oListaFacturas>
                <item>
                    <UUID>{folio}</UUID>
                    <folioFactura>{self.name}</folioFactura>
                    <serie>{serie}</serie>
                    <fechaFactura>{str(self.date)}</fechaFactura>
                    <tipoComprobante>I</tipoComprobante>
                    <moneda>MXN</moneda>
                    <tipoCambio>1</tipoCambio>
                    <subtotal>{self.amount_untaxed}</subtotal>
                    <descuento>0</descuento>
                    <IVA>{self.amount_total-self.amount_untaxed}</IVA>
                    <total>{self.amount_total}</total>
                    <oListaItems>
                    {lines}
                    </oListaItems>
                </item>
                
            </oListaFacturas>
        </item>
        '''
        #motivoDescuento
        return item




