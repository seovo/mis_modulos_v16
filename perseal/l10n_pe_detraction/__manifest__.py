# -*- coding: utf-8 -*-
{
    'name': 'Gestión Detracciones',
    'summary': """ """,

    'description': """
    """,
    'version': "17.20250409",
    'category': 'Localization',
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'depends': [
        'account',
        'account_accountant',
        'l10n_pe_edi',
        'l10n_pe_reports'
    ],
    'data': ['views/account_move_view.xml',
             'views/account_payment_view.xml',
             'wizard/account_payment_register_view.xml'],
    'application': False,
    'license': 'OPL-1',
}