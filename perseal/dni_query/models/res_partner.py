import requests
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat', 'l10n_latam_identification_type_id')
    def _doc_number_change(self):
        if self.vat and self.l10n_latam_identification_type_id.name == 'DNI':
            self.ConsultarDNI(self.vat)
                

    def ConsultarDNI(self, numeroDNI):
        try:
            result = requests.get(f'https://api.apis.net.pe/v1/dni?numero={numeroDNI}')
            if result.status_code == 404:
                self.name = ''
            jsonedResponse = result.json()
            self.name = jsonedResponse['nombres'] + ' ' + jsonedResponse['apellidoPaterno'] + ' ' +  jsonedResponse['apellidoMaterno']
            self.company_type = 'person'
        except Exception as e:
            self.name = ''