# -*- coding: utf-8 -*-

{
    'name': 'POS validacion de numero de serie',
    'summary': """Point Of Sale""",
    'version': '17.20250210',
    'description': """Validacion de la existencia del numero de serie de los productos del pos""",
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    'company': 'Oxe360',
    'category': 'Point of Sale',
    'depends': ['base', 'point_of_sale', 'l10n_pe_pos', 'web'],
    'images': ['static/description/icon.png'],
    "data": [],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_validation_product_series/static/src/**/*',
        ],

    },
    "installable": True,

}