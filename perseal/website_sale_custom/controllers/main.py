# -*- coding: utf-8 -*-

import requests

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        res = super(WebsiteSaleCustom, self).address(**kw)
        print(res)
        l10n_latam_identification_type_ids = request.env['l10n_latam.identification.type'].sudo().search([
            ('l10n_pe_vat_code', 'in', ['0', '1', '6'])
        ])
        res.qcontext.update({
            'l10n_latam_identification_type_ids': l10n_latam_identification_type_ids,
            'l10n_latam_identification_type_id': kw.get('l10n_latam_identification_type_id', '0'),
            'prov_sel': kw.get('prov_sel', '0'),
            'dist_sel': kw.get('dist_sel', '0'),
            'zip': kw.get('zip', ''),
        })
        return res

    def _get_country_related_render_values(self, kw, render_values):
        res = super(WebsiteSaleCustom, self)._get_country_related_render_values(kw, render_values)
        if 'country' in res and not res['country']:
            country_id = request.env['res.country'].search([('code', '=', 'PE')], limit=1)
            mode = render_values['mode']
            res['country'] = country_id
            res['country_states'] = country_id.get_website_sale_states(mode=mode[1])
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(WebsiteSaleCustom, self).checkout_form_validate(mode, all_form_values, data)
        if "vat" not in error:
            if "vat" in data and not data["vat"]:
                error["vat"] = 'missing'
        return error, error_message

    @http.route(['/shop/state_infos/<model("res.country.state"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def state_infos(self, state, **kw):
        city_ids = request.env['res.city'].sudo().search([
            ('state_id', '=', state.id)
        ])
        return dict(cities=[(st.id, st.name) for st in city_ids])

    @http.route(['/shop/city_infos/<model("res.city"):city>'], type='json', auth="public", methods=['POST'], website=True)
    def city_infos(self, city, **kw):
        district_ids = request.env['l10n_pe.res.city.district'].sudo().search([
            ('city_id', '=', city.id)
        ])
        return dict(districts=[(st.id, st.name, st.code) for st in district_ids])

    @http.route(['/shop/consulta_ruc'], type='json', auth="public", methods=['POST'], website=True)
    def consulta_ruc(self, **kw):
        vat = kw.get('vat', False)
        country = kw.get('country', False)
        if vat and country:
            country = int(country)
            URL = 'https://api.apis.net.pe/v1/ruc?numero='
            headers = {
                'accept': '*/*',
                'charset': 'utf-8',
                'accept-encoding': 'gzip,deflate,br',
            }
            res = requests.get("{0}{1}".format(URL, vat.strip()), headers=headers)
            if res.status_code == 200:
                result = res.json()
                data = {}
                name = result.get('nombre', False)
                if name:
                    data['name'] = name
                direccion = result.get('direccion', False)
                if direccion:
                    data['street'] = direccion
                ubigeo = result.get('ubigeo', False)
                if ubigeo and len(ubigeo) == 6:
                    departamento = ubigeo[:2]
                    provincia = ubigeo[0:4]
                    state_id = request.env['res.country.state'].sudo().search([
                        ('code', '=', departamento),
                        ('country_id', '=', country),
                    ], limit=1)
                    if state_id:
                        data['state_id'] = str(state_id.id)
                        city_id = request.env['res.city'].sudo().search([
                            ('l10n_pe_code', '=', provincia),
                            ('state_id', '=', state_id.id),
                            ('country_id', '=', country),
                        ], limit=1)
                        if city_id:
                            data['city_id'] = str(city_id.id)
                            district_id = request.env['l10n_pe.res.city.district'].sudo().search([
                                ('code', '=', ubigeo),
                                ('city_id', '=', city_id.id),
                            ], limit=1)
                            if district_id:
                                data['l10n_pe_district'] = str(district_id.id)
                return data
        return dict(error='Error al ejecutar la consulta RUC')

    def _get_vat_validation_fields(self, data):
        res = super(WebsiteSaleCustom, self)._get_vat_validation_fields(data)
        res['l10n_latam_identification_type_id'] = data['l10n_latam_identification_type_id']
        return res

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg = super(WebsiteSaleCustom, self).values_postprocess(order, mode, values, errors, error_msg)
        new_values['l10n_latam_identification_type_id'] = values.get('l10n_latam_identification_type_id', False)
        new_values['l10n_pe_district'] = values.get('l10n_pe_district', False)
        new_values['city_id'] = values.get('city_id', False)
        return new_values, errors, error_msg
