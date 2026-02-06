# -*- coding: utf-8 -*-
{
    'name': 'Peru - CPE al credito',
    'version': '17.20250408',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""

- se agrega logica para calculo de cuota segun Paymenterm de odooEE

""",
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': [
        'account',
        'base',
        'l10n_pe_edi',
    ],
    'images': ['static/description/icon.jpg'],
    'data': ['security/ir.model.access.csv',
             'views/account_move_view.xml'],
    'application': False,
    'license': 'OPL-1',
}
