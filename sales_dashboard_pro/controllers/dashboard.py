# -*- coding: utf-8 -*-
import json
import io
import xlsxwriter
from odoo import http
from odoo.http import request

class SalesDashboardController(http.Controller):

    @http.route('/sales_dashboard/data', type='json', auth='user', methods=['POST'])
    def get_dashboard_data(self, date_from=None, date_to=None, user_id=None, team_id=None, state=None, product_ids=None, partner_id=None, **kwargs):
        """Returns sales dashboard data by executing queries in the model."""
        return request.env['sales.dashboard'].get_dashboard_data(
            date_from=date_from,
            date_to=date_to,
            salesperson_id=user_id,
            team_id=team_id,
            state=state,
            product_ids=product_ids,
            partner_id=partner_id
        )

    @http.route('/sales_dashboard/filters', type='json', auth='user', methods=['POST'])
    def get_filter_options(self, **kwargs):
        env = request.env
        users = env['res.users'].search([('share', '=', False)], order='name asc')
        teams = env['crm.team'].search([], order='name asc')
        products = env['product.product'].search([('sale_ok', '=', True)], order='name asc', limit=300)
        partners = env['res.partner'].search([('active', '=', True)], order='name asc', limit=300)
        states = [
            {'id': 'draft', 'name': 'Quotation'},
            {'id': 'sent', 'name': 'Quotation Sent'},
            {'id': 'sale', 'name': 'Sales Order'},
            {'id': 'done', 'name': 'Locked'},
            {'id': 'cancel', 'name': 'Cancelled'}
        ]
        return {
            'users': [{'id': u.id, 'name': u.name} for u in users],
            'teams': [{'id': t.id, 'name': t.name} for t in teams],
            'products': [{'id': p.id, 'name': p.name} for p in products],
            'partners': [{'id': pt.id, 'name': pt.name} for pt in partners],
            'states': states,
        }

    @http.route('/sales_dashboard/export_excel', type='http', auth='user')
    def export_excel(self, date_from=None, date_to=None, user_id=None, team_id=None, **kwargs):
        env = request.env
        SaleOrder = env['sale.order'].sudo()
        
        # Build search domain using the same filters
        domain = []
        if date_from and date_from != 'undefined':
            domain.append(('date_order', '>=', date_from))
        if date_to and date_to != 'undefined':
            domain.append(('date_order', '<=', date_to))
        if user_id and user_id != 'undefined':
            domain.append(('user_id', '=', int(user_id)))
        if team_id and team_id != 'undefined':
            domain.append(('team_id', '=', int(team_id)))
            
        orders = SaleOrder.search(domain, order='date_order desc')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Sales Orders')
        
        # Style formatting
        header_format = workbook.add_format({
            'bold': True, 'font_color': 'white', 'bg_color': '#10b981', 
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_format = workbook.add_format({'border': 1})
        num_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})
        
        headers = ['#', 'Order Reference', 'Customer', 'Date', 'Salesperson', 'Sales Team', 'Total Amount', 'Status']
        for col, h in enumerate(headers):
            sheet.write(0, col, h, header_format)
            
        for i, order in enumerate(orders):
            row = i + 1
            sheet.write(row, 0, row, cell_format)
            sheet.write(row, 1, order.name or '', cell_format)
            sheet.write(row, 2, order.partner_id.name if order.partner_id else '', cell_format)
            sheet.write(row, 3, order.date_order.strftime('%d %b %Y') if order.date_order else '', cell_format)
            sheet.write(row, 4, order.user_id.name if order.user_id else '', cell_format)
            sheet.write(row, 5, order.team_id.name if order.team_id else '', cell_format)
            sheet.write_number(row, 6, order.amount_total or 0.0, num_format)
            
            state_label = dict(order._fields['state'].selection).get(order.state, order.state)
            sheet.write(row, 7, state_label, cell_format)
            
        sheet.set_column(1, 4, 20)
        sheet.set_column(5, 7, 15)
        
        workbook.close()
        output.seek(0)
        
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename="Sales_Orders_Report.xlsx"')
            ]
        )
