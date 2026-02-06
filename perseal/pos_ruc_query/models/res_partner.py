# -*- coding: utf-8 -*-

import os
from odoo import models, fields, api, _
import requests
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
import datetime
from io import StringIO, BytesIO


URL = 'https://api.apis.net.pe/v1/ruc?numero='

headers = {
    'accept': '*/*',
    # 'Host': 'e-consultaruc.sunat.gob.pe',
    'charset': 'utf-8',
	'accept-encoding': 'gzip,deflate,br',
    # 'user-agent': 'null'
}

if os.name == 'nt':
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'


class Partner(models.Model):
	_inherit = 'res.partner'
	
	# license_plate = fields.Char()
	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			if 'l10n_latam_identification_type_id' in vals:
				identification_type_ruc_id = self.env['l10n_latam.identification.type'].search([('name', '=', 'RUC')]).id
				if vals['l10n_latam_identification_type_id'] == identification_type_ruc_id:
					vals.update({'is_company': True})
		events = super(Partner, self).create(vals_list)
		return events

	@api.model
	def sunat_data(self, doc_number):
		if len(doc_number) == 8 and self.env['ir.module.module'].sudo().search(
				[('name', '=', 'pos_dni_query')]).state == 'installed':
			return self.get_info_dni(doc_number)
		if len(doc_number) == 11 and self.env['ir.module.module'].sudo().search(
				[('name', '=', 'pos_ruc_query')]).state == 'installed':
			return self.get_info_ruc(doc_number)
		else:
			return False

	def get_info_ruc(self, doc_number):
		# self.ensure_one()

		# doc_number = self.vat
		URL = 'https://api.apis.net.pe/v1/ruc?numero='
		headers = {
			'accept': '*/*',
			'charset': 'utf-8',
			'accept-encoding': 'gzip,deflate,br',
		}
		res = requests.get("{0}{1}".format(URL, doc_number.strip()), headers=headers)
		if res.status_code != 200:
			return False
		result = res.json()
		tnombre = result.get('nombre')
		tstreet = result.get('direccion')
		testado = result.get('estado')
		tprovincia = result.get('provincia')
		tdistrito = result.get('distrito')
		tdepartamento = result.get('departamento')
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
			result['doc_type'] = self.env['l10n_latam.identification.type'].search([('name', '=', 'RUC')]).id
			result['doc_number'] = tdocnumber
			result['country_id'] = self.env['res.country'].search([('code', '=', 'PE')])
			result['country_id'] = result['country_id'] and result['country_id'].id or ''
			district_id = self.env['l10n_pe.res.city.district'].search([('code', '=', tubigeo)])
			result['district_id'] = district_id.id
			result['province_id'] = district_id.city_id.id
			result['state_id'] = district_id.city_id.state_id.id

			# if result['country_id'] and tdepartamento:
			# 	result['state_id'] = self.env['res.country.state'].search([
			# 		('country_id', '=', result['country_id']),
			# 		('name', 'ilike', tdepartamento)
			# 	]).filtered(lambda r: len(r.name) == len(tdepartamento))
			# 	result['state_id'] = result['state_id'] and result['state_id'].id or ''
			#
			# if result.get('state_id') and tprovincia:
			# 	result['province_id'] = self.env['res.city'].search([
			# 		('state_id', '=', result['state_id']),
			# 		('name', 'ilike', tprovincia)
			# 	]).filtered(lambda r: len(r.name) == len(tprovincia))
			# 	result['province_id'] = result['province_id'] and result['province_id'].id or ''
			#
			# if result.get('province_id') and tdistrito:
			# 	result['district_id'] = self.env['l10n_pe.res.city.district'].search([
			# 		('city_id', '=', result['province_id']),
			# 		('name', 'ilike', tdistrito)
			# 	]).filtered(lambda r: len(r.name) == len(tdistrito))
			#
			# 	if result['district_id']:
			# 		result['ubigeo'] = result['district_id'].code or tubigeo
			#
			# 	result['district_id'] = result['district_id'] and result['district_id'].id or ''
			# if tdistrito:
			# 	district = self.env['l10n_pe.res.city.district'].search([('name', 'ilike', tdistrito)])
			# 	result['district_id'] = district.id
			# 	result['province_id'] = district.city_id.id
		return result
