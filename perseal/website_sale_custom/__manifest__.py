# -*- coding: utf-8 -*-
{
    'name': "Website sale custom",
    'description': "Website sale custom",
    'author': 'Oxe360',
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",
    'category': 'Website/Website',
    'version': "17.20230413",
    'depends': [
        'website_sale',
        'l10n_pe',
    ],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_custom/static/src/js/website_sale.js',
        ],
    },
    "installable": True,
}