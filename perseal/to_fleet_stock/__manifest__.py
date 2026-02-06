# -*- coding: utf-8 -*-
{
    'name': "Fleet Stock Consumption",

    'summary': """
Record stock moves with vehicle reference""",

    'description': """
This application integrates the Odoo's Fleet Management application and Inventory to support stock consumption management for your fleet

Key Features
============
1. New Stock Operation Type: Fleet Consumption
2. Record stock consumption (parts, fuel, etc) for your Fleet with Stock Moves as other stock operation
3. Auto generates a vehicle cost if the corresponding stock move moves to a production location that present your vehicles.
4. Keep track of stock that have been consumed for each vehicle

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://ma.tvtmarine.com',
    'live_test_url': 'https://v11demo-int.erponline.vn',
    'support': 'support@ma.tvtmarine.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '17.20240827',

    # any module necessary for this one to work correctly
    'depends': ['fleet', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/stock_data.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/fleet_vehicle_cost_views.xml',
        'data/update_vehicle.sql',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}