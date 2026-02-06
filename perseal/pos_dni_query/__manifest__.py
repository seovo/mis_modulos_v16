# -*- coding: utf-8 -*-

{
    'name': 'Peru - Consulta DNI POS',
    'summary': """Peru - Consulta DNI POS, Point Of Sale""",
    'version': '17.20240603',
    'description': """Este modulo permite consultar informacion por medio del DNI desde el punto de venta""",
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    'company': 'Oxe360',
    'category': 'Point of Sale',
    'depends': ['base', 'point_of_sale', 'l10n_pe_edi', 'l10n_pe_pos', 'web'],
    'images': ['static/description/icon.png'],
    "data": [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_dni_query/static/src/**/*',
        ],

    },
    "installable": True,

}