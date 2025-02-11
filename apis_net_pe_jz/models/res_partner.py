from odoo import api, fields, models
from odoo.exceptions import ValidationError
import requests

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('l10n_latam_identification_type_id','vat')
    def change_apis_net_pe(self):
        for record in self:
            if record.l10n_latam_identification_type_id and record.vat and self.env.company.token_apis_net_pe:
                code = record.l10n_latam_identification_type_id.l10n_pe_vat_code
                #raise ValueError(code)
                if code in ['1','6']:
                    headers = {
                        "Authorization": f"Bearer {self.env.company.token_apis_net_pe}"
                    }
                    if code == '1':
                        url = f"https://api.apis.net.pe/v2/reniec/dni?numero={record.vat}"

                    if code == '6':
                        url = f"https://api.apis.net.pe/v2/sunat/ruc?numero={record.vat}"

                    response = requests.get(url, headers=headers)
                    # Verificar el código de estado de la respuesta
                    if response.status_code == 200:
                        data = response.json()
                        # {'nombres': 'JESÚS', 'apellidoPaterno': 'SANCHEZ', 'apellidoMaterno': 'JIBAJA', 'tipoDocumento': '1', 'numeroDocumento': '60549486', 'digitoVerificador': ''}
                        # Procesar los datos de la respuesta
                        # raise ValidationError(str(data))

                        if code == '1':
                            record.name = data['nombres'] + ' ' + data['apellidoPaterno'] + ' ' + data['apellidoMaterno']
                        else:
                            record.name = data['razonSocial']
                            record.street =  data['direccion'] if 'direccion' in data else ''
                            if 'ubigeo' in data and data['ubigeo']:
                                district = self.env['l10n_pe.res.city.district'].search([('code', '=', data['ubigeo'])])
                                record.l10n_pe_district = district.id
                                record.zip = data['ubigeo']

                            #record.country_id = self.env.ref('base.PE').id

                        '''
                        {
                        "razonSocial":"CONSTRUCTORA TECNOLOGIA MODERNA SOCIEDAD ANONIMA CERRADA",
                        "tipoDocumento":"6","numeroDocumento":"20609030411",
                        "estado":"ACTIVO","condicion":"HABIDO",
                        "direccion":"CAL. DOCTOR CARLOS FERREYROS NRO 528 URB. CORPAC ","ubigeo":"150131","viaTipo":"CAL.",
                        "viaNombre":"DOCTOR CARLOS FERREYROS","zonaCodigo":"URB.","zonaTipo":"CORPAC",
                        "numero":"528","interior":"-","lote":"-","dpto":"-","manzana":"-","kilometro":"-",
                        "distrito":"SAN ISIDRO","prov(base)
                        '''

                    else:
                        try:
                            data = response.json()
                            if 'message' in data:
                                data = data['message']
                            record.name = str(data)
                        except:
                            record.name = str(response)




