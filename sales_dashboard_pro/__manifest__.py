# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard Pro | Odoo Sales Dashboard | Sales Analysis Dashboard | Sales Reports | Sales Board | Sales Charts | CRM Sales | Sales Tracking Dashboard | Sales Analytics | sales funnel, salesperson dashboard, revenue trend, sales kpi',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Premium Sales Dashboard with Total Sales, Invoiced, Quotations, Average Order Value, and Sales Funnel Analytics for Odoo 17',
    'description': """
Sales 360 Dashboard Pro for Odoo 17 is a standalone, fully interactive Sales Intelligence Dashboard.
This module is packed with SEO keywords and features to optimize search:
Keywords: sales, dashboard, analytics, analysis, reports, boards, charts, graph, kpi, pipeline, funnel, trends, forecast, revenue, total sales, invoiced, quotation, average order value, average revenue, products, customers, client, buyer, salesperson, team, manager, supervisor, performance, target, metrics, margins, profit, order count, warehouse, inventory value, stock on hand, leaflet, world map, country distribution, stage distribution, status distribution, donut chart, bar chart, line chart, stock market chart, excel export, pdf print, shareable link, portal view, qr code, whatsapp share, linkedin share, twitter share, email share, modular, fast, custom filters, date range, user filter, partner filter, state filter, interactive dynamic dashboard, odoo 19 sales dashboard, odoo sales report, odoo sales board, sales visualizer, sales monitor, sales tracking, real-time sales dashboard, odoo sales statistics.

Features:
---------
* 7 Premium KPI Cards: Total Revenue, Invoiced, Total Customers, Products Sold, Shipments Done, Open Quotations, Inventory Value
* Stock Market style Sales Trend Line Chart (monthly, last 12 months)
* Order Status Distribution Donut Chart
* Salesperson Performance Horizontal Bar Chart
* Top Customers Leaderboard (Top 3 Customer Cards with avatars, order count, and revenue)
* Pipeline Funnel Chart (order pipeline visualization by stage)
* Top Products Bar Chart (Top 8 products by revenue)
* Recent Orders List View (clickable rows open sale order form)
* Date Range, Salesperson, Partner, and State filters
* Fully compatible with Odoo 17 Community & Enterprise
    """,
    'author': 'Panthera Soft Solutions',
    'company': 'Panthera Soft Solutions',
    'maintainer': 'Panthera Soft Solutions',
    'depends': ['sale', 'sale_management', 'stock', 'web', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_dashboard_views.xml',
        'views/portal_templates.xml',
        'views/report_sales_dashboard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sales_dashboard_pro/static/src/lib/chart.umd.min.js',
            'sales_dashboard_pro/static/src/scss/sales_dashboard.scss',
            'sales_dashboard_pro/static/src/xml/sales_dashboard.xml',
            'sales_dashboard_pro/static/src/js/sales_dashboard.js',
        ],
    },
    'images': ['static/description/main_screen.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
