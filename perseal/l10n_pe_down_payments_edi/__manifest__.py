# -*- coding: utf-8 -*-
{
    'name': 'Gestión Anticipos',
    'summary': """Facturacion electronica anticipos""",

    'description': """Facturacion electronica anticipos
    """,
    'version': "17.20240528",
    'category': 'Localization',
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'depends': [
        'account',
        'l10n_pe_edi',
        'account_edi_ubl_cii',
    ],
    'data': ['data/product_template_data.xml',
             'views/res_config_settings_views.xml',
             'views/account_move.xml',
             'data/ubl_20_templates.xml',],
    'application': False,
    'license': 'OPL-1',
}