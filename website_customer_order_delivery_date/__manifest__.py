# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    "name": "Customer Order Delivery Date",
    "author": "AppJetty",
    'license': 'OPL-1',
    "version": "17.0",
    "category": "Website",
    "website": "https://www.appjetty.com/",
    "description": "This module is used for add customer order delivery date section at payment page",
    "summary": "Know when your customers want products delivered",
    "depends": ['website_sale','sale_management'],
    "data": [
            'views/customer_order_delivery_config_view.xml',
            'views/sale_order_view.xml',
            'views/template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_customer_order_delivery_date/static/src/js/website_customer_order_delivery_date.js',
        ],
    },
    'images': ['static/description/order-delivery-date-comments-profile.png'],
    'installable': True,
    'auto_install': False,
    'support': 'support@appjetty.com',
}
