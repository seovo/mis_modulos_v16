# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de compras simplificado electronico 8.3",

    'summary': """
        Ple de compras simplificado electronico 8.3""",

    'description': """
        Ple de compras simplificado electronico 8.3
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
    'demo': [],
    'installable': False,
}
