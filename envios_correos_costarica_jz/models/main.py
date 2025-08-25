# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging

from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request, route
from odoo.addons.base.models.ir_qweb_fields import nl2br_enclose
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.sale.controllers import portal as sale_portal
from odoo.osv import expression
from odoo.tools import lazy, str2bool
from odoo.tools.json import scriptsafe as json_scriptsafe

_logger = logging.getLogger(__name__)

class WebsiteSale(payment_portal.PaymentPortal):

    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'],
                website=True)
    def country_infos(self, country, mode, **kw):
        states = [(0,'Seleccione',0)] + [(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode)]
        return dict(
            fields=country.get_address_fields(),
            states=states,
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    @http.route(
        ['/shop/canton_infos/<model("res.country.county"):county>'], type="json", auth="public", methods=["POST"], website=True
    )
    def cantons_infos(self, county, **kw):
        districts = request.env["res.country.district"].sudo().search([("county_id", "=", county.id)])
        return {'districts': [(d.id, d.name, d.code) for d in districts]}

    @http.route(
        ['/shop/state_infos_cr/<model("res.country.state"):state>'],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def state_infos_cr(self, state, **kw):
        states = request.env["res.country.county"].sudo().search([("state_id", "=", state.id)])
        return {'cantons': [(c.id, c.name, c.code) for c in states]}

    def _get_mandatory_fields_billing(self, country_id=False):

        res = super()._get_mandatory_fields_billing(country_id)
        if request.website.sudo().company_id.country_id.code != "CR":
            return res

        req = ["name", "email", "street", "city", "country_id", "vat", "l10n_latam_identification_type_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            #if country.zip_required:
            #    req += ['zip']

            if country_id == request.website.sudo().company_id.country_id.id:
                req += ["county_id"]
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        res = super()._get_mandatory_fields_shipping(country_id)
        if request.website.sudo().company_id.country_id.code != "CR":
            return res
        req = ["name", "street", "city", "country_id", "phone"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            #if country.zip_required:
            #    req += ['zip']
            if country_id == request.website.sudo().company_id.country_id.id:
                req += ["county_id"]
        return req


    def _get_country_related_render_values(self, kw, render_values):

        res = super()._get_country_related_render_values(kw, render_values)

        values = render_values["checkout"]

        state = "state_id" in values \
                and values["state_id"] != "" \
                and request.env["res.country.state"].browse(int(values["state_id"]))
        county = "county_id" in values \
               and values["county_id"] != "" \
               and request.env["res.country.county"].browse(int(values["county_id"]))



        mode = render_values['mode']
        order = render_values['website_sale_order']
        country = res['country']

        if state:
            cantons = request.env['res.country.county'].sudo().search([('state_id', '=', state.id)])
            res.update({'cantons': cantons})

            if county:
                districts = request.env['res.country.district'].sudo().search([('county_id', '=', county.id)])
                res.update({'districts': districts})

        #type_documents
        type_documents =  request.env['l10n_latam.identification.type'].sudo().search([])
        if type_documents:
            res.update({'type_documents': type_documents})

        #type_documents
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):

        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        order.update_price_carrier_cr()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))
        if order._is_public_order():
            mode = ('new', 'billing')
            can_edit_vat = True
        else:  # IF ORDER LINKED TO A PARTNER
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    # If we modify the main customer of the SO ->
                    # 'billing' bc billing requirements are higher than shipping ones
                    can_edit_vat = order.partner_id.can_edit_vat()
                    mode = ('edit', 'billing')
                else:
                    address_mode = kw.get('mode')
                    if not address_mode:
                        if partner_id == order.partner_invoice_id.id:
                            address_mode = 'billing'
                        elif partner_id == order.partner_shipping_id.id:
                            address_mode = 'shipping'

                    # Make sure the address exists and belongs to the customer of the SO
                    partner_sudo = Partner.browse(partner_id).exists()
                    partners_sudo = Partner.search(
                        [('id', 'child_of', order.partner_id.commercial_partner_id.ids)]
                    )
                    mode = ('edit', address_mode)
                    if address_mode == 'billing':
                        billing_partners = partners_sudo.filtered(lambda p: p.type != 'delivery')
                        if partner_sudo not in billing_partners:
                            raise Forbidden()
                    elif address_mode == 'shipping':
                        shipping_partners = partners_sudo.filtered(lambda p: p.type != 'invoice')
                        if partner_sudo not in shipping_partners:
                            raise Forbidden()

                    can_edit_vat = partner_sudo.can_edit_vat()

                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', kw.get('mode') or 'shipping')
            else:  # no mode - refresh without post?
                order.update_price_carrier_cr()
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":
            pre_values = self.values_preprocess(kw)
            #raise ValueError(pre_values)


            if 'vat' in pre_values:
                pre_values['vat'] = str(pre_values['vat']).strip()

            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                update_mode, address_mode = mode
                partner_id = self._checkout_form_save(mode, post, kw)
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id

                fpos_before = order.fiscal_position_id
                update_values = {}
                if update_mode == 'new':  # New address
                    if order._is_public_order():
                        update_values['partner_id'] = partner_id

                    if address_mode == 'billing':
                        update_values['partner_invoice_id'] = partner_id
                        if kw.get('use_same'):
                            update_values['partner_shipping_id'] = partner_id
                        elif (
                                order._is_public_order()
                                and not kw.get('callback')
                                and not order.only_services
                        ):
                            # Now that the billing is set, if shipping is necessary
                            # request the customer to fill the shipping address
                            kw['callback'] = '/shop/address'
                    elif address_mode == 'shipping':
                        update_values['partner_shipping_id'] = partner_id
                elif update_mode == 'edit':  # Updating an existing address
                    if order.partner_id.id == partner_id:
                        # Editing the main partner of the SO --> also trigger a partner update to
                        # recompute fpos & any partner-related fields
                        update_values['partner_id'] = partner_id

                    if address_mode == 'billing':
                        update_values['partner_invoice_id'] = partner_id
                        if not kw.get('callback') and not order.only_services:
                            kw['callback'] = '/shop/checkout'
                    elif address_mode == 'shipping':
                        update_values['partner_shipping_id'] = partner_id

                order.write(update_values)
                order.update_price_carrier_cr()



                if order.fiscal_position_id != fpos_before:
                    # Recompute taxes on fpos change
                    # TODO recompute all prices too to correctly manage price_include taxes ?
                    order._recompute_taxes()

                if 'partner_id' in update_values:
                    # Force recomputation of pricelist on main customer address update
                    request.website.sale_get_order(update_pricelist=True)

                # TDE FIXME: don't ever do this
                # -> TDE: you are the guy that did what we should never do in commit e6f038a
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        is_public_user = request.website.is_public_user()

        #raise ValueError(values['county_id'])

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'account_on_checkout': request.website.account_on_checkout,
            'is_public_user': is_public_user,
            'is_public_order': order._is_public_order(),
            'use_same': is_public_user or ('use_same' in kw and str2bool(kw.get('use_same') or '0')),
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)


    def values_postprocess(self, order, mode, values, errors, error_msg):
        post, errors, error_msg = super().values_postprocess(order, mode, values, errors, error_msg)
        website = request.env['website'].get_current_website()
        # This is needed so that the field is correctly write on the partner
        if values.get('county_id') and website.company_id.country_code == 'CR':
            post['county_id'] = values['county_id']
        if values.get('district_id') and website.company_id.country_code == 'CR':
            post['district_id'] = values['district_id']

        if values.get('l10n_latam_identification_type_id'):
            post['l10n_latam_identification_type_id'] = values['l10n_latam_identification_type_id']

        if values.get('vat'):
            post['vat'] = str(values['vat']).strip()



        return post, errors, error_msg
