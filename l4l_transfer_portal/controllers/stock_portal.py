# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import http, _, SUPERUSER_ID, models, fields
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.addons.portal.controllers import portal
from odoo.exceptions import UserError, MissingError, AccessError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from odoo.addons.portal.controllers.mail import _message_post_helper


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'transfer_count' in counters:
            company_id = request.env.context.get('allowed_company_ids')
            user_id = request.env.user
            values['transfer_count'] = request.env['stock.picking'].sudo().search_count(
                [('company_id', 'in', company_id), ('user_id', '=', user_id.id)])
        return values

    def get_transfer_searchbar_sortings(self):
        return {
            'date': {'label': _('Scheduled Date'), 'order': 'scheduled_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Status'), 'order': 'state'},
        }

    def get_transfer_searchbar_filters(self):
        today = datetime.now().today()
        yesterday = today - relativedelta(days=1)
        today_date_str = today.strftime('%Y-%m-%d')
        last_month_end = today - relativedelta(day=1)
        last_month_start = last_month_end - relativedelta(months=1)
        last_week_start = today - relativedelta(weeks=1)
        first_day_current_year = datetime(datetime.now().year, 1, 1)
        first_day_last_year = first_day_current_year - relativedelta(years=1)
        next_month_start = (today + relativedelta(months=1)).replace(day=1)
        this_month_end = next_month_start - relativedelta(days=1)
        this_week_start = today - relativedelta(days=today.weekday())
        this_week_end = this_week_start + relativedelta(days=6)
        this_year_start = today.replace(day=1, month=1)
        this_year_end = this_year_start + relativedelta(years=1)

        domain_last_month = [
            ('scheduled_date', '>=', last_month_start.strftime('%Y-%m-%d')),
            ('scheduled_date', '<', last_month_end.strftime('%Y-%m-%d'))]
        domain_last_week = [
            ('scheduled_date', '>=', last_week_start.strftime('%Y-%m-%d')),
            ('scheduled_date', '<', today.strftime('%Y-%m-%d'))]
        domain_last_year = [
            ('scheduled_date', '>=', first_day_last_year.strftime('%Y-%m-%d')),
            ('scheduled_date', '<', first_day_current_year.strftime('%Y-%m-%d'))]
        domain_this_month = [
            ('scheduled_date', '>=', today.replace(day=1).strftime('%Y-%m-%d')),
            ('scheduled_date', '<=', this_month_end.strftime('%Y-%m-%d'))]
        domain_today = [('scheduled_date', '>', yesterday.strftime('%Y-%m-%d')),
                        ('scheduled_date', '<=', today_date_str)]
        domain_this_week = [
            ('scheduled_date', '>=', this_week_start.strftime('%Y-%m-%d')),
            ('scheduled_date', '<=', this_week_end.strftime('%Y-%m-%d'))]
        domain_this_year = [
            ('scheduled_date', '>=', this_year_start.strftime('%Y-%m-%d')),
            ('scheduled_date', '<=', this_year_end.strftime('%Y-%m-%d'))]
        return {
            'All': {'label': _('All'), 'domain': []},
            'Old Date': {'label': _('Last Month'), 'domain': domain_last_month},
            'Last Week': {'label': _('Last Week'), 'domain': domain_last_week},
            'Last Year': {'label': _('Last Year'), 'domain': domain_last_year},
            'This Month': {'label': _('This Month'), 'domain': domain_this_month},
            'Today': {'label': _('Today'), 'domain': domain_today},
            'This Week': {'label': _('This Week'), 'domain': domain_this_week},
            'This Year': {'label': _('This Year'), 'domain': domain_this_year},
        }

    def get_transfer_searchbar_groupby(self):
        return {
            'none': {'input': 'none', 'label': _('None'), "order": 1},
            'partner_id': {'input': 'partner_id', 'label': _('Contact'), "order": 1},
            'picking_type_id': {'input': 'picking_type_id', 'label': _('Operation Type'), "order": 1},
            'state': {'input': 'state', 'label': _('State'), "order": 1},
        }

    @http.route(["/transfer_detail"], type='http', auth='user', website=True)
    def create_transfer_details(self, sortby='name', filterby='All', search="", search_in="all", groupby="none",
                                **kw):
        company_id = request.env.context.get('allowed_company_ids')
        searchbar_sortings = self.get_transfer_searchbar_sortings()
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        search_list = {
            'All': {'label': _('All'), 'input': 'All', 'domain': []},
            'Reference': {'label': _('Reference'), 'input': 'Reference', 'domain': [('name', 'ilike', search)]},
            'Scheduled Date': {'label': _('Scheduled Date'), 'input': 'Scheduled Date',
                               'domain': [('scheduled_date', 'ilike', search)]},
            'Contact': {'label': _('Contact'), 'input': 'Contact', 'domain': [('partner_id', 'ilike', search)]},
            'Source Document': {'label': _('Source Document'), 'input': 'Source Document',
                                'domain': [('origin', 'ilike', search)]},
        }
        if search_in not in search_list:
            search_in = 'All'
        search_domain = search_list[search_in]['domain']
        searchbar_filters = self.get_transfer_searchbar_filters()
        if filterby == 'All':
            domain = []
        else:
            domain = searchbar_filters[filterby]['domain']
        if not groupby:
            groupby = 'none'
        searchbar_groupby = self.get_transfer_searchbar_groupby()
        transfer_group_by = searchbar_groupby.get(groupby, {})
        if groupby in ('partner_id', 'picking_type_id', 'state'):
            transfer_group_by = transfer_group_by.get('input')
        else:
            transfer_group_by = ''
        transfer_obj = request.env['stock.picking']
        transfer_detail = request.env['stock.picking'].sudo().search(
            [('company_id', 'in', company_id), ('user_id', '=', request.env.user.id)] + search_domain + domain,
            order=order)
        if transfer_group_by:
            transfer_group_list = [{transfer_group_by: key, 'transfer': transfer_obj.concat(*group)} for key, group in
                                   groupbyelem(transfer_detail, itemgetter(transfer_group_by))]
        else:
            transfer_group_list = [{'transfer': transfer_detail}]
        return request.render(
            'l4l_transfer_portal.l4l_portal_transfer_details',
            {
                'default_url': '/transfer_detail',
                'transfer': transfer_detail,
                'sortby': sortby,
                'groupby': groupby,
                'filterby': filterby,
                'group_transfer': transfer_group_list,
                'page_name': 'transfer_details_view',
                'search_in': search_in,
                'search': search,
                'searchbar_inputs': search_list,
                'searchbar_sortings': searchbar_sortings,
                'searchbar_groupby': searchbar_groupby,
                'searchbar_filters': searchbar_filters,
            }
        )

    @http.route(["/transfer_detail/<model('stock.picking'):record>"], type='http', auth="public", website=True)
    def transfer_record_details(self, record):
        transfer_details_rec = request.env['stock.picking'].sudo().browse(record)
        transfer_lines_details_rec = request.env['stock.move'].sudo().search(
            [('picking_id', '=', record.id)])
        return http.request.render(
            'l4l_transfer_portal.l4l_portal_transfer_record_details',
            {'transfer_detail_rec': transfer_details_rec.id,
             'transfer_lines_detail_rec': transfer_lines_details_rec,
             'page_name': 'transfer_details_view_rec',
             'stock_picking': record}
        )

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        ReportAction = request.env['ir.actions.report'].sudo()

        if hasattr(model, 'company_id'):
            if len(model.company_id) > 1:
                raise UserError(_('Multi company reports are not supported.'))
            ReportAction = ReportAction.with_company(model.company_id)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(ReportAction, method_name)(report_ref, list(model.ids), data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)

    @http.route(["/transfer_detail/download_stock_pdf/<model('stock.picking'):record>"], type='http', auth="public",
                website=True)
    def download_stock_pdf(self, record, **kw):
        return self._show_report(model=record, report_type='pdf', report_ref='stock.action_report_delivery',
                                 download=True)

    @http.route(["/transfer_detail/stock_pdf/<model('stock.picking'):record>"], type='http', auth="public",
                website=True)
    def stock_pdf(self, record, **kw):
        return self._show_report(model=record, report_type='pdf', report_ref='stock.action_report_delivery',
                                 download=False)

    @http.route(["/transfer_detail/<model('stock.picking'):record>/accept"], type='json', auth="public", website=True)
    def transfer_detail_sigm(self, record, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        # try:
        #    order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        # except (AccessError, MissingError):
        #    return {'error': _('Invalid order.')}

        # if not order_sudo._has_to_be_signed():
        #    return {'error': _('The order is not in a state requiring customer signature.')}
        # if not signature:
        #    return {'error': _('Signature is missing.')}

        #order_sudo = request.env['project.task'].sudo().search([('id', '=', int(task_id))])
        order_sudo = record

        try:
            order_sudo.sudo().write({
                # 'signed_by': name,
                # 'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        # if not order_sudo._has_to_be_paid():
        #    order_sudo.action_confirm()
        #    order_sudo._send_order_confirmation_mail()

        # pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [order_sudo.id])[
        #    0]
        _message_post_helper(
            'stock.picking',
            order_sudo.id,
            _('Firmado por %s', name),
            # attachments=[('%s.pdf' % order_sudo.name, pdf)],
            token=access_token,
        )

        query_string = '&message=sign_ok'
        # if order_sudo._has_to_be_paid():
        #    query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }
