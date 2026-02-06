# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de compras electronico 8.2",

    'summary': """
        Ple de compras 8.2""",

    'description': """
        Ple de compras 8.2
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
        # 'views/report_ple_8_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
