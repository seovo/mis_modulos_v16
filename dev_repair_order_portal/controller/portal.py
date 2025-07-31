# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from collections import OrderedDict
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        repair_orders = request.env['repair.order'].sudo()
        repair_order_count = repair_orders.search_count([
            ('partner_id', '=', partner.id),
        ])
        values.update({
            'repair_order_count': repair_order_count,
        })
        return values

    @http.route(['/my/repair_order', '/my/repair_order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_repair_order(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        repair_order_obj = request.env['repair.order'].sudo()

        domain = []    
        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(today) + datetime.timedelta(days=7))
        week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
        month_ago = (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        starting_of_year = datetime.datetime.now().date().replace(month=1, day=1)    
        ending_of_year = datetime.datetime.now().date().replace(month=12, day=31)

        def sd(date):
            return fields.Datetime.to_string(date)
        def previous_week_range(date):
            start_date = date + datetime.timedelta(-date.weekday(), weeks=-1)
            end_date = date + datetime.timedelta(-date.weekday() - 1)
            return {'start_date':start_date.strftime('%Y-%m-%d %H:%M:%S'), 'end_date':end_date.strftime('%Y-%m-%d %H:%M:%S')}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [('create_date', '>=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),('create_date', '<=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]},
            'yesterday':{'label': _('Yesterday'), 'domain': [('create_date', '>=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00')),('create_date', '<=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))]},
            'week': {'label': _('This Week'),
                     'domain': [('create_date', '>=', (datetime.datetime.today() + relativedelta(days=-today.weekday())).strftime('%Y-%m-%d')), ('create_date', '<=', this_week_end_date)]},
            'last_seven_days':{'label':_('Last 7 Days'),
                         'domain': [('create_date', '>=', sd(week_ago)), ('create_date', '<=', sd(datetime.datetime.today()))]},
            'last_week':{'label':_('Last Week'),
                         'domain': [('create_date', '>=', previous_week_range(datetime.datetime.today()).get('start_date')), ('create_date', '<=', previous_week_range(datetime.datetime.today()).get('end_date'))]},
            
            'last_month':{'label':_('Last 30 Days'),
                         'domain': [('create_date', '>=', month_ago), ('create_date', '<=', sd(datetime.datetime.today()))]},
            'month':{'label': _('This Month'),
                    'domain': [
                       ("create_date", ">=", sd(today.replace(day=1))),
                       ("create_date", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))
                    ]
                },
            'year':{'label': _('This Year'),
                    'domain': [
                       ("create_date", ">=", sd(starting_of_year)),
                       ("create_date", "<=", sd(ending_of_year)),
                    ]
                }
        }
        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('All')},
            'state': {'input': 'state', 'label': _('State')},
            'product': {'input': 'product', 'label': _('Product')},
        }

        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if not sortby:
            sortby = 'create_date'

        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        repair_order_count = repair_order_obj.search_count(domain)
        pager = portal_pager(
            url = "/my/repair_order",
            url_args = {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total = repair_order_count,
            page = page,
            step = self._items_per_page
        )
        repair_order = repair_order_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_repair_order_history'] = repair_order.ids[:100]
        if groupby == 'product':
            grouped_repair_order = [request.env['repair.order'].concat(*g) for k, g in groupbyelem(repair_order, itemgetter('product_id'))]
        elif groupby == 'state':
            grouped_repair_order = [request.env['repair.order'].concat(*g) for k, g in groupbyelem(repair_order, itemgetter('state'))]
        else:
            grouped_repair_order = [repair_order]

        values.update({
            'date': date_begin,
            'repair_orders': repair_order,
            'grouped_repair_orders': grouped_repair_order,
            'page_name': 'repair_order',
            'pager': pager,
			'default_url': '/my/repair_order',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby':searchbar_groupby,
            'filterby': filterby,
            'sortby': sortby,
            'groupby': groupby,
        })
        return request.render("dev_repair_order_portal.portal_my_repair_order", values)

    @http.route(['/my/repair_order/<int:repair_order_id>'], type='http', auth="public", website=True)
    def portal_repair_order_page(self, repair_order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            repair_order_sudo = self._document_check_access('repair.order', repair_order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
 
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=repair_order_sudo, report_type=report_type, report_ref='repair.action_report_repair_order', download=download)

        now = fields.Date.today()
        if repair_order_sudo and request.session.get('view_repair_order_%s' % repair_order_sudo.id) != now and request.env.user.share and access_token:
            request.session['view_event_%s' % repair_order_sudo.id] = now
            body = _('Repair Order viewed by customer')
            # _message_post_helper(res_model='repair.order', res_id=repair_order_sudo.id, message=body, token=repair_order_sudo.access_token, message_type='notification', subtype="mail.mt_note", partner_ids=repair_order_sudo.partner_id.ids)
        values = {
            'repair_order': repair_order_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': repair_order_sudo.partner_id.id,
            'report_type': 'html',
        }
        if repair_order_sudo.company_id:
            values['res_company'] = repair_order_sudo.company_id

        history = request.session.get('my_event_history', [])
        values.update(get_records_pager(history, repair_order_sudo))
        return request.render('dev_repair_order_portal.repair_order_portal_template', values)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
