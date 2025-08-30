from odoo import _, fields, models , api
from odoo.exceptions import UserError, ValidationError
import requests
import json
import xmltodict


class ResPartner(models.Model):
    _inherit = 'res.partner'




class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def create(self,vals):
        res = super().create(vals)

        if len(res.sale_order_ids) == 1:
            if res.sale_order_ids.carrier_id.is_correo_costarica:
                res.sale_order_ids.generate_number_guia()

        #raise ValueError(res.sale_order_ids)
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    log_costarica      = fields.Text(copy=False)
    has_send_guia_cr   = fields.Boolean(string="Enviado?",copy=False)
    pdf_guia_costarica = fields.Binary(copy=False)
    name_pdf_guia_costarica = fields.Char(copy=False)


    def update_price_carrier_cr(self):
        #raise ValueError('holaaa')
        for record in self:
            if record.carrier_id.is_correo_costarica:
                for line in record.order_line:
                    if line.is_delivery:
                        carrier_amount = record.carrier_id.get_amount_envios_cr(record)
                        line.price_unit = carrier_amount


    def get_tracking_costarica(self):
        token = self.carrier_id.generate_token_ccr()

        # PY001936481CR

        # consultar tracking
        url = self.carrier_id.url_soap
        headers = {
            "Authorization": token,
            'SOAPAction': 'http://tempuri.org/IwsAppCorreos/ccrMovilTracking',
            'Content-Type': 'text/xml; charset=utf-8',
        }

        xml_data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:ccrMovilTracking>
                 <tem:NumeroEnvio>{self.client_order_ref}</tem:NumeroEnvio>
              </tem:ccrMovilTracking>
           </soapenv:Body>
        </soapenv:Envelope>'''

        response = requests.post(url, data=xml_data, headers=headers)

        xml_dict = xmltodict.parse(response.text)
        json_response = json.dumps(xml_dict, indent=4)
        self.log_costarica = str(json_response) + str(response.status_code)




    def generate_number_guia(self,token=None):

        if not self.carrier_id.is_correo_costarica:
            return

        if not token:
            token = self.carrier_id.generate_token_ccr()

        url = self.carrier_id.url_soap
        headers = {
            "Authorization": token,
            'SOAPAction': 'http://tempuri.org/IwsAppCorreos/ccrGenerarGuia',
            'Content-Type': 'text/xml; charset=utf-8',
        }
        xml_data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
                           <soapenv:Header/>
                           <soapenv:Body>
                              <tem:ccrGenerarGuia/>
                           </soapenv:Body>
                        </soapenv:Envelope>'''

        response = requests.post(url, data=xml_data, headers=headers)

        if response.status_code != 200:
            raise ValueError([response, xml_data , headers])
        xml_dict = xmltodict.parse(response.text)
        json_response = json.dumps(xml_dict, indent=4)
        json_obj = json.loads(json_response)
        envio_id = json_obj['s:Envelope']['s:Body']['ccrGenerarGuiaResponse']['ccrGenerarGuiaResult'][
            'a:NumeroEnvio']
        self.client_order_ref = envio_id

        self.has_send_guia_cr = False
        self.pdf_guia_costarica = False
        self.name_pdf_guia_costarica =  False

    def action_confirm(self):
        res = super().action_confirm()
        if self.carrier_id.is_correo_costarica:
            self.generate_guia()

        return res

    def generate_guia(self):
        if self.transaction_ids and self.carrier_id :

            from unidecode import unidecode

            if  self.has_send_guia_cr:
                self.get_tracking_costarica()
                return



            envio_id = self.client_order_ref



            if not envio_id:
                # generar guia
                self.generate_number_guia()
                envio_id = self.client_order_ref

            #raise ValueError(self.shipping_weight)

            shi = self.partner_shipping_id
            comp = self.company_id.partner_id

            if not shi.district_id:
                raise ValidationError('Indicar Distrito')


            #raise ValueError(datenow.strftime('%Y-%m-%dT%H:%M:%S'))
            #2024-12-18 02:06:44
            #'''2024-11-14T11:10:21'''

            adreess = f'''{shi.street or '' } {shi.street2 or '' } {shi.state_id.name} {shi.county_id.name} {shi.district_id.name}'''
            adreess_comp = f'''{comp.street or ''} {comp.street2 or ''} {comp.state_id.name} {comp.county_id.name} {comp.district_id.name}'''
            #raise ValueError(adreess)
            #raise ValueError(self.amount_delivery)





            amount_delivery = int(self.amount_delivery * 100)



            zip = f'{shi.state_id.code}{shi.county_id.code}{shi.district_id.code}'
            zipcomp = f'{comp.state_id.code}{comp.county_id.code}{comp.district_id.code}'

            datenow = fields.Datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            weight = int(self.shipping_weight)

            observacion = self.name


            adreess = adreess

            xml_data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"  xmlns:tem="http://tempuri.org/" xmlns:wsap="http://schemas.datacontract.org/2004/07/wsAppCorreos">
	<soapenv:Header/>
	<soapenv:Body>
		<tem:ccrRegistroEnvio>
			<tem:ccrReqEnvio>
				<wsap:Cliente>{self.carrier_id.cod_cliente_costarica}</wsap:Cliente>
				<wsap:Envio>
					<wsap:COD_CLIENTE>{self.carrier_id.cod_cliente_costarica}</wsap:COD_CLIENTE>
					<wsap:DEST_APARTADO>{zip}</wsap:DEST_APARTADO>
					<wsap:DEST_DIRECCION>{unidecode(adreess)}</wsap:DEST_DIRECCION>
					<wsap:DEST_NOMBRE>{unidecode(shi.name)}</wsap:DEST_NOMBRE>
					<wsap:DEST_TELEFONO>{shi.phone}</wsap:DEST_TELEFONO>
					<wsap:DEST_ZIP>{zip}</wsap:DEST_ZIP>
					<wsap:ENVIO_ID>{envio_id}</wsap:ENVIO_ID>
					<wsap:FECHA_ENVIO>{datenow}</wsap:FECHA_ENVIO>
					<wsap:MONTO_FLETE>{amount_delivery}</wsap:MONTO_FLETE>
					<wsap:OBSERVACIONES>{unidecode(observacion)}</wsap:OBSERVACIONES>
					<wsap:PESO>{weight}</wsap:PESO>
					<wsap:SEND_DIRECCION>{unidecode(adreess_comp)}</wsap:SEND_DIRECCION>
					<wsap:SEND_NOMBRE>{unidecode(comp.name)}</wsap:SEND_NOMBRE>
					<wsap:SEND_TELEFONO>{comp.phone}</wsap:SEND_TELEFONO>
					<wsap:SEND_ZIP>{zipcomp}</wsap:SEND_ZIP>
					<wsap:SERVICIO>{self.carrier_id.servicio_costarica}</wsap:SERVICIO>
					<wsap:USUARIO_ID>{self.carrier_id.usuario_id_costarica}</wsap:USUARIO_ID>
				</wsap:Envio>
			</tem:ccrReqEnvio>
		</tem:ccrRegistroEnvio>
	</soapenv:Body>
</soapenv:Envelope>'''

            #xml_dict2 = xmltodict.parse(xml_data)
            #self.log_costarica = xml_data
            #return

            #xml_dict = xmltodict.parse(xml_data)
            #json_response = str(json.dumps(xml_dict, indent=4))
            #self.log_costarica = str(json_response)
            #return

            ########################3

            token = self.carrier_id.generate_token_ccr()

            # registrar envio

            urlx = self.carrier_id.url_soap

            headers = {
                "Authorization": token,
                'SOAPAction': 'http://tempuri.org/IwsAppCorreos/ccrRegistroEnvio',
                'Content-Type': 'text/xml; charset=utf-8',
            }

            try:
                responsex = requests.post(urlx, data=xml_data.encode('utf-8'), headers=headers)
            except:

                xml_dict = xmltodict.parse(xml_data)
                json_response = str(json.dumps(xml_dict, indent=4))
                self.log_costarica = str(json_response)




            if responsex.status_code == 200 :
                xml_dict = xmltodict.parse(responsex.text)
                json_response = json.dumps(xml_dict, indent=4)



                json_obj = json.loads(json_response)
                pdf = json_obj['s:Envelope']['s:Body']['ccrRegistroEnvioResponse']['ccrRegistroEnvioResult']['a:PDF']


                self.has_send_guia_cr = True
                try:
                    self.pdf_guia_costarica = pdf
                    self.name_pdf_guia_costarica = f'Envio_{envio_id}'
                except:
                    xml_dict = xmltodict.parse(xml_data)
                    json_responsex = str(json.dumps(xml_dict, indent=4))
                    self.log_costarica = str(json_response)+str(json_responsex)+str(responsex.status_code)
                    return




            else:
                xml_dict = xmltodict.parse(xml_data)
                json_response = str(json.dumps(xml_dict, indent=4))


            self.log_costarica = str(json_response)+str(responsex.status_code)
            #raise ValueError([responsex.status_code,responsex.text,xml_data])


            #pass
            #registrar envio

