# -*- coding: utf-8 -*-
{
    'name': 'Website Shopping Clear Cart',
    'summary': "Website Shopping Clear Cart",
    'description': """Website Shopping Clear Cart'""",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Website',
    'version': '17.0.0.1.0',
    'depends': ['website_sale'],
    'data': [
        'views/templates.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'website_clear_cart/static/src/js/website_sale.js',
        ],
    },

    'license': "OPL-1",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/clear_cart.png'],
    'pre_init_hook': 'pre_init_check',
}
