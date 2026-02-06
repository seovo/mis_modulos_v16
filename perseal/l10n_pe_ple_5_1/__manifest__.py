# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro diario electronico 5.1",

    'summary': """
        Ple de diario 5.1""",

    'description': """
        Ple de diario 5.1
    """,

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    'category': 'Accountig',
    'version': '17.20230124',
    'depends': ['l10n_pe_ple',
                'l10n_latam_invoice_document',
                #'l10n_pe_edi_extended',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/report_ple_5_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
