# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import json
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


class SalesDashboard(models.TransientModel):
    _name = 'sales.dashboard'
    _description = 'Sales Performance Dashboard'

    @api.model
    def get_dashboard_data(self, date_from=None, date_to=None, salesperson_id=None, team_id=None, state=None, product_ids=None, partner_id=None):
        # ── Build base domain ───────────────────────────────────────────────
        domain = []
        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))
        if salesperson_id:
            domain.append(('user_id', '=', int(salesperson_id)))
        if team_id:
            domain.append(('team_id', '=', int(team_id)))
        if state:
            domain.append(('state', '=', state))
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
        if product_ids:
            domain.append(('order_line.product_id', 'in', product_ids))

        SaleOrder = self.env['sale.order'].sudo()
        company_currency = self.env.company.currency_id

        # ── Core Order Sets ─────────────────────────────────────────────────
        all_orders      = SaleOrder.search(domain)
        confirmed_orders = SaleOrder.search(domain + [('state', 'in', ('sale', 'done'))])
        quotations       = SaleOrder.search(domain + [('state', 'in', ('draft', 'sent'))])

        # ── KPI 1: Total Revenue ─────────────────────────────────────────────
        total_revenue = sum(confirmed_orders.mapped('amount_total'))

        # ── KPI 2: Total Invoiced ─────────────────────────────────────────────
        invoiced = 0.0
        if confirmed_orders:
            invoices = confirmed_orders.invoice_ids.filtered(
                lambda m: m.state == 'posted' and m.move_type == 'out_invoice'
            )
            invoiced = sum(invoices.mapped('amount_total'))

        # ── KPI 3: Total Customers (unique partners in confirmed) ─────────────
        unique_customers = len(set(confirmed_orders.mapped('partner_id').ids))

        # ── KPI 4: Products Sold (unique product count from order lines) ──────
        order_lines = confirmed_orders.mapped('order_line')
        products_sold_qty = sum(order_lines.mapped('product_uom_qty'))
        unique_products   = len(set(order_lines.mapped('product_id').ids))

        # ── KPI 5: Shipments (delivered stock pickings) ───────────────────────
        Picking = self.env['stock.picking'].sudo()
        picking_domain = [('state', '=', 'done'), ('picking_type_code', '=', 'outgoing')]
        if date_from:
            picking_domain.append(('date_done', '>=', date_from))
        if date_to:
            picking_domain.append(('date_done', '<=', date_to))
        shipments_done  = Picking.search_count(picking_domain)
        # Pending shipments
        picking_pending = [('state', 'in', ('assigned', 'waiting', 'confirmed')), ('picking_type_code', '=', 'outgoing')]
        shipments_pending = Picking.search_count(picking_pending)

        # ── KPI 6: Open Quotations Count ─────────────────────────────────────
        open_quotations_count = len(quotations)
        quotation_value       = sum(quotations.mapped('amount_total'))

        # ── KPI 7: Warehouse / Inventory Value ───────────────────────────────
        Warehouse = self.env['stock.warehouse'].sudo()
        warehouses = Warehouse.search([])
        warehouse_count = len(warehouses)
        # Total inventory value (quant on-hand)
        Quant = self.env['stock.quant'].sudo()
        quants = Quant.search([('location_id.usage', '=', 'internal')])
        inventory_value = sum(q.value for q in quants if q.value)

        # ── KPI 8: Average Order Value (AOV) ─────────────────────────────────
        aov = total_revenue / len(confirmed_orders) if confirmed_orders else 0.0

        # ── KPI 9: Net Revenue (Untaxed) ─────────────────────────────────────
        net_revenue = sum(confirmed_orders.mapped('amount_untaxed'))

        # ── KPI 10: Tax Amount ────────────────────────────────────────────────
        tax_amount = sum(confirmed_orders.mapped('amount_tax'))

        # ── KPI 11: Conversion Rate ───────────────────────────────────────────
        conversion_rate = (len(confirmed_orders) / len(all_orders) * 100.0) if all_orders else 0.0

        currency_info = {
            'symbol': company_currency.symbol,
            'position': company_currency.position,
        }

        # ─────────────────────────────────────────────────────────────────────
        # CHART 1: Monthly Revenue Trend (Last 12 Months)
        # ─────────────────────────────────────────────────────────────────────
        today = date.today()
        trend_labels, trend_sales, trend_quotes = [], [], []
        for i in range(11, -1, -1):
            d = today - relativedelta(months=i)
            month_start = date(d.year, d.month, 1)
            next_month  = month_start + relativedelta(months=1)
            m_confirmed = SaleOrder.search(domain + [
                ('state', 'in', ('sale', 'done')),
                ('date_order', '>=', fields.Datetime.to_string(month_start)),
                ('date_order', '<',  fields.Datetime.to_string(next_month)),
            ])
            m_quotes = SaleOrder.search(domain + [
                ('state', 'in', ('draft', 'sent')),
                ('date_order', '>=', fields.Datetime.to_string(month_start)),
                ('date_order', '<',  fields.Datetime.to_string(next_month)),
            ])
            trend_labels.append(d.strftime('%b %Y'))
            trend_sales.append(sum(m_confirmed.mapped('amount_total')))
            trend_quotes.append(sum(m_quotes.mapped('amount_total')))

        # ─────────────────────────────────────────────────────────────────────
        # CHART 2: Order Status Distribution (Donut)
        # ─────────────────────────────────────────────────────────────────────
        states_count = {'draft': 0, 'sent': 0, 'sale': 0, 'done': 0, 'cancel': 0}
        for order in all_orders:
            if order.state in states_count:
                states_count[order.state] += 1

        donut_colors = ['#6ee7b7', '#34d399', '#10b981', '#059669', '#ef4444']
        status_dist = [
            {'label': 'Quotation',     'value': states_count['draft'],  'color': '#6ee7b7'},
            {'label': 'Sent',          'value': states_count['sent'],   'color': '#34d399'},
            {'label': 'Sale Order',    'value': states_count['sale'],   'color': '#10b981'},
            {'label': 'Locked',        'value': states_count['done'],   'color': '#059669'},
            {'label': 'Cancelled',     'value': states_count['cancel'], 'color': '#ef4444'},
        ]
        donut_labels = [x['label'] for x in status_dist if x['value'] > 0]
        donut_values = [x['value'] for x in status_dist if x['value'] > 0]
        donut_clrs   = [x['color'] for x in status_dist if x['value'] > 0]

        # ─────────────────────────────────────────────────────────────────────
        # CHART 3: Salesperson Performance Bar
        # ─────────────────────────────────────────────────────────────────────
        sp_data = {}
        for order in confirmed_orders:
            sp = order.user_id.name or 'Unassigned'
            sp_data[sp] = sp_data.get(sp, 0.0) + order.amount_total
        sorted_sp = sorted(sp_data.items(), key=lambda x: x[1], reverse=True)[:7]
        salesperson_labels = [x[0] for x in sorted_sp]
        salesperson_values = [x[1] for x in sorted_sp]

        # ─────────────────────────────────────────────────────────────────────
        # CHART 4: Sales Pipeline Funnel
        # ─────────────────────────────────────────────────────────────────────
        invoiced_orders_count = len(confirmed_orders.invoice_ids.filtered(
            lambda m: m.state == 'posted' and m.move_type == 'out_invoice'
        ))
        funnel_data = [
            {'stage': 'Quotations',      'value': len(quotations)},
            {'stage': 'Confirmed Orders','value': len(confirmed_orders)},
            {'stage': 'Shipped',         'value': shipments_done},
            {'stage': 'Invoiced',        'value': invoiced_orders_count},
        ]
        funnel_colors = ['#6ee7b7', '#34d399', '#10b981', '#059669']
        funnel_labels = [x['stage'] for x in funnel_data]
        funnel_values = [x['value'] for x in funnel_data]

        # ─────────────────────────────────────────────────────────────────────
        # CHART 5: Customer Map — Country Distribution
        # ─────────────────────────────────────────────────────────────────────
        country_map = {}
        for order in all_orders:
            country = order.partner_id.country_id
            if country:
                key = country.name
                if key not in country_map:
                    country_map[key] = {
                        'country': country.name,
                        'code': country.code or '',
                        'lat': 0.0,
                        'lng': 0.0,
                        'orders': 0,
                        'revenue': 0.0,
                    }
                country_map[key]['orders'] += 1
                if order.state in ('sale', 'done'):
                    country_map[key]['revenue'] += order.amount_total

        # Approximate lat/lng for common countries
        COUNTRY_COORDS = {
            'India': (20.5937, 78.9629), 'United States': (37.0902, -95.7129),
            'United Kingdom': (55.3781, -3.4360), 'Germany': (51.1657, 10.4515),
            'France': (46.2276, 2.2137), 'Australia': (-25.2744, 133.7751),
            'Canada': (56.1304, -106.3468), 'Brazil': (-14.2350, -51.9253),
            'China': (35.8617, 104.1954), 'Japan': (36.2048, 138.2529),
            'UAE': (23.4241, 53.8478), 'Saudi Arabia': (23.8859, 45.0792),
            'Singapore': (1.3521, 103.8198), 'South Africa': (-30.5595, 22.9375),
            'Russia': (61.5240, 105.3188), 'Mexico': (23.6345, -102.5528),
            'Argentina': (-38.4161, -63.6167), 'Netherlands': (52.1326, 5.2913),
            'Spain': (40.4637, -3.7492), 'Italy': (41.8719, 12.5674),
            'Turkey': (38.9637, 35.2433), 'Pakistan': (30.3753, 69.3451),
            'Bangladesh': (23.6850, 90.3563), 'Nigeria': (9.0820, 8.6753),
            'Egypt': (26.8206, 30.8025), 'Indonesia': (-0.7893, 113.9213),
            'Malaysia': (4.2105, 101.9758), 'Thailand': (15.8700, 100.9925),
            'Philippines': (12.8797, 121.7740), 'Vietnam': (14.0583, 108.2772),
            'Kenya': (-0.0236, 37.9062), 'Ethiopia': (9.1450, 40.4897),
            'Ghana': (7.9465, -1.0232), 'Poland': (51.9194, 19.1451),
            'Belgium': (50.5039, 4.4699), 'Sweden': (60.1282, 18.6435),
            'Norway': (60.4720, 8.4689), 'Denmark': (56.2639, 9.5018),
            'Switzerland': (46.8182, 8.2275), 'Portugal': (39.3999, -8.2245),
            'Czech Republic': (49.8175, 15.4730), 'Romania': (45.9432, 24.9668),
            'Ukraine': (48.3794, 31.1656), 'Israel': (31.0461, 34.8516),
            'Iran': (32.4279, 53.6880), 'Iraq': (33.2232, 43.6793),
            'Kuwait': (29.3117, 47.4818), 'Oman': (21.4735, 55.9754),
            'Qatar': (25.3548, 51.1839), 'Jordan': (30.5852, 36.2384),
            'Morocco': (31.7917, -7.0926), 'Algeria': (28.0339, 1.6596),
            'Tunisia': (33.8869, 9.5375), 'Libya': (26.3351, 17.2283),
            'New Zealand': (-40.9006, 174.8860), 'Ireland': (53.1424, -7.6921),
            'Finland': (61.9241, 25.7482), 'Austria': (47.5162, 14.5501),
            'Hungary': (47.1625, 19.5033), 'Greece': (39.0742, 21.8243),
            'Serbia': (44.0165, 21.0059), 'Croatia': (45.1000, 15.2000),
        }
        customer_map_data = []
        for key, val in country_map.items():
            coords = COUNTRY_COORDS.get(key)
            if coords:
                val['lat'] = coords[0]
                val['lng'] = coords[1]
            customer_map_data.append(val)
        customer_map_data.sort(key=lambda x: x['orders'], reverse=True)

        # ─────────────────────────────────────────────────────────────────────
        # TOP 3 PARTNERS (Orders Count & Revenue with image and name)
        # ─────────────────────────────────────────────────────────────────────
        partner_revenue = {}
        partner_orders = {}
        for order in confirmed_orders:
            partner = order.partner_id
            if not partner:
                continue
            partner_revenue[partner] = partner_revenue.get(partner, 0.0) + order.amount_total
            partner_orders[partner] = partner_orders.get(partner, 0) + 1

        sorted_top_3 = sorted(partner_revenue.items(), key=lambda x: x[1], reverse=True)[:3]
        top_3_products_data = []
        for index, (partner, revenue) in enumerate(sorted_top_3):
            top_3_products_data.append({
                'rank': index + 1,
                'id': partner.id,
                'name': partner.name,
                'qty': partner_orders.get(partner, 0),
                'revenue': revenue,
                'image_url': f'/web/image/res.partner/{partner.id}/image_128',
            })

        # ─────────────────────────────────────────────────────────────────────
        # CHART 7: Product Category Distribution (Pie Chart)
        # ─────────────────────────────────────────────────────────────────────
        category_revenue = {}
        for line in order_lines:
            cat = line.product_id.categ_id
            cat_name = cat.name if cat else 'Uncategorized'
            category_revenue[cat_name] = category_revenue.get(cat_name, 0.0) + line.price_subtotal

        sorted_categories = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)
        top_categories = sorted_categories[:5]
        other_revenue = sum(x[1] for x in sorted_categories[5:])
        if other_revenue > 0:
            top_categories.append(('Others', other_revenue))

        category_pie_labels = [x[0] for x in top_categories]
        category_pie_values = [x[1] for x in top_categories]

        product_sales = {}
        for line in order_lines:
            pname = line.product_id.name or 'Unknown'
            product_sales[pname] = product_sales.get(pname, 0.0) + line.price_subtotal
        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:8]
        product_labels = [x[0] for x in sorted_products]
        product_values = [x[1] for x in sorted_products]

        # ─────────────────────────────────────────────────────────────────────
        # PIVOT: Status × Salesperson
        # ─────────────────────────────────────────────────────────────────────
        all_active_users = self.env['res.users'].search([('share', '=', False)])
        pivot_users = []
        for sp in all_active_users:
            sp_orders = all_orders.filtered(lambda o, s=sp: o.user_id == s)
            if sp_orders:
                pivot_users.append(sp.name)
        pivot_users = pivot_users[:8]

        status_keys   = ['draft', 'sent', 'sale', 'done', 'cancel']
        status_labels = ['Quotation', 'Sent', 'Sale Order', 'Locked', 'Cancelled']
        matrix, stage_totals, user_totals, grand_total = [], [], [0] * len(pivot_users), 0
        for sk in status_keys:
            row_orders = all_orders.filtered(lambda o, s=sk: o.state == s)
            row, row_sum = [], 0
            for ui, uname in enumerate(pivot_users):
                cnt = len(row_orders.filtered(lambda o, u=uname: (o.user_id.name or 'Unassigned') == u))
                row.append(cnt)
                user_totals[ui] += cnt
                row_sum += cnt
                grand_total += cnt
            matrix.append(row)
            stage_totals.append(row_sum)

        # ─────────────────────────────────────────────────────────────────────
        # RECENT ORDERS
        # ─────────────────────────────────────────────────────────────────────
        recent_orders_list = []
        for order in SaleOrder.search(domain, order='date_order desc', limit=10):
            recent_orders_list.append({
                'id': order.id,
                'name': order.name,
                'partner': order.partner_id.name or 'Unknown',
                'date': order.date_order.strftime('%d %b %Y') if order.date_order else '',
                'amount_total': order.amount_total,
                'state': order.state,
                'user': order.user_id.name or '',
            })

        # ─────────────────────────────────────────────────────────────────────
        # FILTER OPTIONS
        # ─────────────────────────────────────────────────────────────────────
        salespersons_list = [{'id': u.id, 'name': u.name} for u in self.env['res.users'].search([('share', '=', False)])]
        teams_list = [{'id': t.id, 'name': t.name} for t in self.env['crm.team'].search([])]

        return {
            # ── Enterprise KPI Cards ──────────────────────────────────────────────
            'total_revenue':       total_revenue,
            'invoiced':            invoiced,
            'total_customers':     unique_customers,
            'products_sold_qty':   round(products_sold_qty, 0),
            'unique_products':     unique_products,
            'shipments_done':      shipments_done,
            'shipments_pending':   shipments_pending,
            'open_quotations':     open_quotations_count,
            'quotation_value':     quotation_value,
            'warehouse_count':     warehouse_count,
            'inventory_value':     inventory_value,
            'aov':                 aov,
            'net_revenue':         net_revenue,
            'tax_amount':          tax_amount,
            'conversion_rate':     round(conversion_rate, 1),
            'currency':            currency_info,

            # ── Charts ───────────────────────────────────────────────────
            'revenue_trend': {
                'labels': trend_labels,
                'values': trend_sales,
                'quotes': trend_quotes,
            },
            'stage_donut': {
                'labels': donut_labels,
                'values': donut_values,
                'colors': donut_clrs,
            },
            'salesperson': {
                'labels': salesperson_labels,
                'values': salesperson_values,
            },
            'funnel': {
                'labels': funnel_labels,
                'values': funnel_values,
                'colors': funnel_colors[:len(funnel_labels)],
            },
            'category_pie': {
                'labels': category_pie_labels,
                'values': category_pie_values,
            },
            'top_3_products_data': top_3_products_data,
            'customer_map': customer_map_data,
            'top_products': {
                'labels': product_labels,
                'values': product_values,
            },
            'pivot': {
                'stages':       status_labels,
                'users':        pivot_users,
                'matrix':       matrix,
                'stage_totals': stage_totals,
                'user_totals':  user_totals,
                'grand_total':  grand_total,
            },
            'recent_orders': recent_orders_list,
            'salespersons':  salespersons_list,
            'teams':         teams_list,
        }
