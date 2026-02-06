# -*- coding: utf-8 -*-
{
    'name': 'Peru - Facturacion Nubefact',
    'version': '17.20250522',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""
    Facturacion através de Nubefact para Perú
    """,
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': [
        'account',
        'web',
        'l10n_pe_edi'
    ],
    'images': ['static/description/icon.jpg'],
    'data': ["views/res_config_settings_views.xml",
    ],
    'application': False,
    'license': 'OPL-1',
}