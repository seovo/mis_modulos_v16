from odoo import api, fields, models

import requests
# URL del servicio SOAP
url = 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php'
import hashlib
from datetime import datetime
import pytz

import http.client


class AccountMove(models.Model):
    _inherit = "account.move"

    def generar_token(self,numero_dt):
        # Establecer la zona horaria
        timezone = pytz.timezone('America/Mexico_City')
        # Obtener la fecha y hora actual en la zona horaria especificada
        ahora = datetime.now(timezone)
        # Formatear la fecha y hora como 'YYYYMMDDHH'
        fecha_formateada = ahora.strftime('%Y%m%d%H')

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
            #'Content-Type': 'text/xml; charset=utf-8',
            'Content-Type': 'text/xml',
            'SOAPAction': 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php#enviarDetalleVenta'
        }


        # Crear el cuerpo de la petición SOAP


        soap_body = f'''<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php">
           <soapenv:Body>
             <tns:enviarDetalleVenta>
                 <tns:usuario>alfen_t</tns:usuario>
                 <tns:password>PwSnil91p_Pb7q9Z</tns:password>
                 <tns:token>{token_generado}</tns:token>
                 <tns:numeroDT>{numero_dt}</tns:numeroDT>
                 <tns:nombreDT>SERVICIOS INDUSTRIALES ALFEN</tns:nombreDT>
                 <tns:oListaClientes>
                 </tns:oListaClientes>
             </tns:enviarDetalleVenta>
           </soapenv:Body>
        </soapenv:Envelope>'''

        response = requests.post(url, data=soap_body, headers=headers)
        # Mostrar la respuesta
        raise ValueError(response.text)
        print(response.text)



