import requests

# URL del servicio SOAP
url = 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php'


import hashlib
from datetime import datetime
import pytz

def generar_token(numero_dt):
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

# Ejemplo de uso
numero_dt = 43006
token_generado = generar_token(numero_dt)
print(f"Token generado: {token_generado}")


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


soapenv_body = f'''<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php">
           <soapenv:Body>
             <tns:enviarDetalleVenta>
                 <tns:usuario>alfen_t</tns:usuario>
                 <tns:password>PwSnil91p_Pb7q9Z</tns:password>
                 <tns:token>{token_generado}</tns:token>
                 <tns:numeroDT>{numero_dt}</tns:numeroDT>
                 <tns:nombreDT>SERVICIOS INDUSTRIALES ALFEN</tns:nombreDT>
                 <tns:oListaClientes>
                     <tns:item>
                         <tns:clienteFinal>123456</tns:clienteFinal>
                         <tns:RFC>ABCDE123456789</tns:RFC>
                         <tns:razonSocial>Razón Social del Cliente</tns:razonSocial>
                         <tns:codigoPostal>12345</tns:codigoPostal>
                         <tns:colonia>Colonia Ejemplo</tns:colonia>
                         <tns:calle>Calle Ejemplo</tns:calle>
                         <tns:numeroExterior>123</tns:numeroExterior>
                         <tns:tipoNegocioArea>ARMADORA</tns:tipoNegocioArea>
                         <tns:areaEmpresarial>Area Ejemplo</tns:areaEmpresarial>
                         
                
                     </tns:item>
                     
                 </tns:oListaClientes>
             </tns:enviarDetalleVenta>
           </soapenv:Body>
        </soapenv:Envelope>'''


# Establecer los headers
headers = {
    'Content-Type': 'text/xml; charset=utf-8',
    'SOAPAction': 'https://ws.smcmx.com.mx/wssmc_test/smcmx_service_test.php#enviarDetalleVenta'
}

# Enviar la petición
response = requests.post(url, data=soap_body, headers=headers)

# Mostrar la respuesta
print(response.text)
