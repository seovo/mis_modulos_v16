from odoo import api, fields, models

import requests
# URL del servicio SOAP
url = 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php'
import hashlib


from datetime import datetime, timedelta
import pytz

import http.client




class AccountMove(models.Model):
    _inherit = "account.move"

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

        # Ejemplo de uso
        numero_dt = '43006'
        token_generado = self.generar_token(numero_dt)
        print(f"Token generado: {token_generado}")

        # Establecer los headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            #'Content-Type': 'text/xml',
            'SOAPAction': 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php#enviarDetalleVenta'
        }


        # Crear el cuerpo de la petición SOAP






        soap_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php">
    <soap:Body>
        <tns:enviarDetalleVenta>
            <usuario>alfen_t</usuario>
            <password>PwSnil91p_Pb7q9Z</password>
            <token>{token_generado}</token>
            <numeroDT>{numero_dt}</numeroDT>
            <nombreDT>SERVICIOS INDUSTRIALES ALFEN</nombreDT>
            <oListaClientes>
                <item>
                    <clienteFinal>123456</clienteFinal>
                    <RFC>ABCDE123456789</RFC>
                    <razonSocial>Razón Social del Cliente</razonSocial>
                    <codigoPostal>12345</codigoPostal>
                    <colonia>Colonia Ejemplo</colonia>
                    <calle>Calle Ejemplo</calle>
                    <numeroExterior>123</numeroExterior>
                    <tipoNegocioArea>ARMADORA</tipoNegocioArea>
                    <areaEmpresarial>Area Ejemplo</areaEmpresarial>
                </item>
            </oListaClientes>
        </tns:enviarDetalleVenta>
    </soap:Body>
</soap:Envelope>'''



        response = requests.post(url, data=soap_body.encode('utf-8'), headers=headers)
        # Mostrar la respuesta
        raise ValueError(response.text)
        print(response.text)


