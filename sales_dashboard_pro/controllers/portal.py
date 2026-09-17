# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from .dashboard import SalesDashboardController

class SalesDashboardPortalController(http.Controller):

    @http.route('/sales-dashboard', type='http', auth='user', website=True)
    def share_portal_dashboard(self, date_from=None, date_to=None, user_id=None, team_id=None, **kwargs):
        env = request.env
        dc = SalesDashboardController()
        data = dc.get_dashboard_data(date_from=date_from, date_to=date_to, user_id=user_id, team_id=team_id)
        
        company = env.company
        currency = company.currency_id
        def format_currency(value):
            if currency.position == 'before':
                return f"{currency.symbol}{value:,.2f}"
            else:
                return f"{value:,.2f} {currency.symbol}"

        pivot = data.get('pivot', {})
        users = pivot.get('users', [])
        mat_data = pivot.get('matrix', [])
        matrix = []
        for ui, uname in enumerate(users):
            row = {'salesperson': uname}
            total = 0
            for si, sk in enumerate(['draft', 'sent', 'sale', 'done', 'cancel']):
                val = mat_data[si][ui] if si < len(mat_data) and ui < len(mat_data[si]) else 0
                row[sk] = val
                total += val
            row['total'] = total
            matrix.append(row)

        flat_vals = []
        for r in matrix:
            flat_vals.extend([r['draft'], r['sent'], r['sale'], r['done'], r['cancel']])
        pivot_max = max(flat_vals) if flat_vals else 1

        values = {
            'company': company,
            'currency': currency,
            'total_sales': data.get('total_revenue', 0.0),
            'quotation_value': data.get('quotation_value', 0.0),
            'invoiced': data.get('invoiced', 0.0),
            'aov': data.get('aov', 0.0),
            'pivot_data': matrix,
            'pivot_max': pivot_max,
            'recent': data.get('recent_orders', []),
            'format_currency': format_currency,
            'dashboard_data_json': json.dumps({
                'trend_labels': data.get('revenue_trend', {}).get('labels', []),
                'trend_sales': data.get('revenue_trend', {}).get('values', []),
                'trend_quotes': data.get('revenue_trend', {}).get('quotes', []),
                'status_distribution': data.get('stage_donut', {}).get('values', []),
                'salesperson_labels': data.get('salesperson', {}).get('labels', []),
                'salesperson_values': data.get('salesperson', {}).get('values', []),
                'funnel_data': data.get('funnel', {}).get('values', []),
            })
        }
        return request.render('sales_dashboard_pro.portal_share_dashboard', values)

    @http.route('/sales-dashboard/print-pdf', type='http', auth='user')
    def print_pdf_dashboard(self, date_from=None, date_to=None, user_id=None, team_id=None, **kwargs):
        env = request.env
        dc = SalesDashboardController()
        data = dc.get_dashboard_data(date_from=date_from, date_to=date_to, user_id=user_id, team_id=team_id)

        user_name = env['res.users'].browse(int(user_id)).name if user_id else 'All'
        team_name = env['crm.team'].browse(int(team_id)).name if team_id else 'All'

        company = env.company
        currency = company.currency_id
        def format_currency(value):
            if currency.position == 'before':
                return f"{currency.symbol}{value:,.2f}"
            else:
                return f"{value:,.2f} {currency.symbol}"

        pivot = data.get('pivot', {})
        users = pivot.get('users', [])
        mat_data = pivot.get('matrix', [])
        matrix = []
        for ui, uname in enumerate(users):
            row = {'salesperson': uname}
            total = 0
            for si, sk in enumerate(['draft', 'sent', 'sale', 'done', 'cancel']):
                val = mat_data[si][ui] if si < len(mat_data) and ui < len(mat_data[si]) else 0
                row[sk] = val
                total += val
            row['total'] = total
            matrix.append(row)

        flat_vals = []
        for r in matrix:
            flat_vals.extend([r['draft'], r['sent'], r['sale'], r['done'], r['cancel']])
        pivot_max = max(flat_vals) if flat_vals else 1

        values = {
            'date_from': date_from,
            'date_to': date_to,
            'user_name': user_name,
            'team_name': team_name,
            'total_sales': data.get('total_revenue', 0.0),
            'quotation_value': data.get('quotation_value', 0.0),
            'invoiced': data.get('invoiced', 0.0),
            'aov': data.get('aov', 0.0),
            'pivot_data': matrix,
            'pivot_max': pivot_max,
            'recent': data.get('recent_orders', []),
            'format_currency': format_currency,
        }

        # Render PDF report via Odoo report actions
        pdf_content, _ = env['ir.actions.report']._render_qweb_pdf(
            'sales_dashboard_pro.action_report_sales_dashboard',
            [1],
            data=values
        )

        return request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'inline; filename="Sales_Dashboard_Report.pdf"')
            ]
        )
