# -*- coding: utf-8 -*-
{
    'name': 'Peru - Reporte CPE',
    'version': '17.20250522',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""
    Formato de Reporte Facturacion PE
    """,
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': [
        'account',
        'web',
        'l10n_pe_edi'
    ],
    'images': ['static/description/icon.jpg'],
    'data': [
        'data/ir_ui_view.xml',
        'views/account_move_view.xml',
        'report/account_report.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}
