# -*- coding: utf-8 -*-

import requests

from odoo import models, fields, api, _


class Partner(models.Model):
	_inherit = 'res.partner'

	sunat_state = fields.Char(string='Estado Sunat')
	taxpayer_condition = fields.Char(string='Condición del contribuyente')

	def sunat_data_backend(self):
		self.ensure_one()
		doc_number = self.vat
		URL = 'https://api.apis.net.pe/v1/ruc?numero='
		headers = {
			'accept': '*/*',
			'charset': 'utf-8',
			'accept-encoding': 'gzip,deflate,br',
		}
		res = requests.get("{0}{1}".format(URL, doc_number.strip()), headers=headers)
		if res.status_code != 200:
			return {
				'warning': {
					'title': _("Warning"),
					'message': _('Impossible to recover information for this RUC, please complete manually')
				}
			}
		result = res.json()
		tnombre = result.get('nombre')
		tstreet = result.get('direccion')
		testado = result.get('estado')
		tcondition = result.get('condicion')
		tubigeo = result.get('ubigeo')
		tdoctype = result.get('tipoDocumento')
		tdocnumber = result.get('numeroDocumento')
		if tnombre and tstreet and testado:
			result['name'] = tnombre
			result['fiscal_name'] = tnombre
			result['street'] = tstreet
			result['sunat_state'] = testado
			result['taxpayer_condition'] = tcondition
			result['doc_type'] = tdoctype
			result['doc_number'] = tdocnumber
			result['country_id'] = self.env['res.country'].search([('code', '=', 'PE')])
			result['country_id'] = result['country_id'] and result['country_id'].id or ''
			district_id = self.env['l10n_pe.res.city.district'].search([('code', '=', tubigeo)])
			result['district_id'] = district_id.id
			result['province_id'] = district_id.city_id.id
			result['state_id'] = district_id.city_id.state_id.id
		return result


	@api.onchange('vat',  'l10n_latam_identification_type_id')
	def _vat_onchange(self):
		if self.vat and self.l10n_latam_identification_type_id.name == 'RUC':
			result = self.sudo().sunat_data_backend()
			self.name = result.get('name')
			self.country_id = result.get('country_id')
			self.state_id = result.get('state_id')
			self.city_id = result.get('province_id')
			self.l10n_pe_district = result.get('district_id')
			self.street = result.get('street')
			self.zip = result.get('ubigeo')
			self.sunat_state = result.get('estado')
			self.taxpayer_condition = result.get('condicion')

	@api.onchange('city_id')
	def _onchange_city_id(self):
		if self.city_id:
			self.city = self.city_id.name
			self.state_id = self.city_id.state_id
		elif self._origin:
			self.city = False
			self.state_id = False

