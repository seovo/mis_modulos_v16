# -*- coding: utf-8 -*-
{
    'name': 'Peru - Reporte de cuotas',
    'version': '15.0.20240103',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""


""",
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': ['account',
                'account_invoice_pdf',
                'l10n_pe_credit_payments',
    ],
    'images': ['static/description/icon.jpg'],
    'data': [
        'views/report_invoice_dml.xml'
    ],
    'application': False,
    'license': 'OPL-1',
}
