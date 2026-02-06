import requests
from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def sunat_data(self, doc_number):
        if len(doc_number) == 8 and self.env['ir.module.module'].sudo().search([('name', '=', 'pos_dni_query')]).state == 'installed':
            return self.get_info_dni(doc_number)
        if len(doc_number) == 11 and self.env['ir.module.module'].sudo().search([('name', '=', 'pos_ruc_query')]).state == 'installed':
            return self.get_info_ruc(doc_number)
        else:
            return False

    def get_info_dni(self, doc_number):
        try:
            result = requests.get(f'https://api.apis.net.pe/v1/dni?numero={doc_number}')
            if result.status_code == 404:
                return False
            jsonedResponse = result.json()
            result = {'nombre': jsonedResponse['nombres'] + ' ' + jsonedResponse['apellidoPaterno'] + ' ' +  jsonedResponse['apellidoMaterno'],
                      'province_id': '',
                      'country_id': '',
                      'doc_type': self.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')]).id,
                      'district_id': '',
                      'state_id': '',
                      'street': '',
                      'ubigeo': ''}
            return result
        except Exception as e:
            raise UserError(e)