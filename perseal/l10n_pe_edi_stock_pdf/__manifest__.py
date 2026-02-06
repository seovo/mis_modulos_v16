# -*- coding: utf-8 -*-
{
    "name": """Peruvian - Electronic Delivery Note PDF""",
    'version': '17.20250326',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""
    Formato de Reporte Facturacion PE
    """,
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': [
        'stock',
        'web',
        'l10n_pe_edi_stock',
        'delivery',
    ],
    'images': ['static/description/icon.jpg'],
    'data': [
             'report/stock_piking_template.xml',
             'report/stock_piking_report.xml',
    ],
    'application': False,
    'license': 'OPL-1',
    'post_init_hook': '_stock_post_init',
}