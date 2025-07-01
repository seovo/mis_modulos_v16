from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError
import requests
import json

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    is_correo_costarica = fields.Boolean()
    username_costarica = fields.Char()
    password_costarica = fields.Char()
    sistema_costarica = fields.Char()
    cod_cliente_costarica =  fields.Char()
    usuario_id_costarica =  fields.Char()
    servicio_costarica = fields.Char()
    url_token = fields.Char(string="Url Token")
    url_soap = fields.Char(string="Url SOAP")

    def generate_token_ccr(self):
        url = self.url_token

        # Diccionario con los parámetros
        data = {
            "Username": self.username_costarica,
            "Password": self.password_costarica,
            "Sistema": self.sistema_costarica
        }

        headers = {
            "Content-Type": "application/json",  # Indica que el cuerpo de la solicitud es JSON
            "Accept": "application/json"  # Indica que esperas una respuesta en JSON
        }

        # Realizar la solicitud POST

        response = requests.post(url, json=data, headers=headers, verify=False)

        #raise ValueError([response,response.status_code,response.text])

        if response.status_code == 200:
            # response_data = response.json()
            return response.text

        return None

    def get_amount_envios_cr(self,order):
        import xmltodict
        amount = 0

        # response_data = response.json()
        token = self.generate_token_ccr()

        if token:
            peso = 0
            for line in order.order_line:
                if line.product_id and not line.is_delivery:
                    peso += (line.product_id.weight * 1000 ) * line.product_uom_qty

            peso = int(peso)


            #raise ValueError(peso)

            canton_destino = order.partner_shipping_id.county_id.code

            canton_origen = order.company_id.partner_id.county_id.code

            provincia_origen = order.company_id.partner_id.state_id.code

            provincia_destino = order.partner_shipping_id.state_id.code

            urlx = self.url_soap

            xml_data = f'''<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                           <Header/>
                           <Body>
                              <ccrTarifa xmlns="http://tempuri.org/">
                                 <reqTarifa>
                                    <CantonDestino xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{canton_destino}</CantonDestino>
                                    <CantonOrigen xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{canton_origen}</CantonOrigen>
                                    <Peso xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{peso}</Peso>
                                    <ProvinciaDestino xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{provincia_destino}</ProvinciaDestino>
                                    <ProvinciaOrigen xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{provincia_origen}</ProvinciaOrigen>
                                    <Servicio xmlns="http://schemas.datacontract.org/2004/07/wsAppCorreos">{int(self.servicio_costarica)}</Servicio>
                                 </reqTarifa>
                              </ccrTarifa>
                           </Body>
                        </Envelope>'''
            headers = {
                "Authorization": token,
                'SOAPAction': 'http://tempuri.org/IwsAppCorreos/ccrTarifa',
                # "Content-Type": "text/xml" ,  # Especificamos que el contenido es XML
                'Content-Type': 'text/xml; charset=utf-8',
                # "Accept": "application/json"  # Indica que esperas una respuesta en JSON
            }
            # Realizar la solicitud POST
            responsex = requests.post(urlx, data=xml_data, headers=headers)

            if responsex.status_code != 200:
                raise ValueError([urlx,responsex, headers, xml_data])
            # warning_message = responsex.text
            # warning_message = str([headers,responsex.text])
            xml_dict = xmltodict.parse(responsex.text)

            # Convertir diccionario a JSON
            json_response = json.dumps(xml_dict, indent=4)
            json_obj = json.loads(json_response)
            result = json_obj['s:Envelope']['s:Body']['ccrTarifaResponse']['ccrTarifaResult']
            amount = float(result['a:MontoTarifa']) + float(result['a:Impuesto'])
            # warning_message = json_response

        return amount



    def rate_shipment(self, order):

        #raise ValueError('QUE PASAS')
        if self.is_correo_costarica:
            warning_message = False

            amount = self.get_amount_envios_cr(order)



            return {
                'success': True,
                'price': amount,
                'error_message': False,
                'warning_message': warning_message
            }



        return super().rate_shipment(order)


