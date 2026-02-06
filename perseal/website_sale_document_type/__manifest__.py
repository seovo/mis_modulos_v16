# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    "name": "Seleccionar tipo de documento",
    "author": "Oxe360",
    'license': 'LGPL-3',
    "version": "17.20240325",
    "category": "Website",
    "website": "http://www.oxe360.com",
    "description": "Seleccionar tipo comprobante en las compras por el sitio web",
    "summary": "Seleccionar tipo comprobante en las compras por el sitio web",
    "depends": ['website_sale',
                'sale_management'],
    "data": [
        'views/template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_document_type/static/src/js/website_customer_order_comment.js'
        ],
    },
    'installable': True,
    'auto_install': False,
    'support': 'http://www.oxe360.com',
}