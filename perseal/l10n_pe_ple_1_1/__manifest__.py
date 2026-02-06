# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de caja y bancos - Detalle de los movimientos del efectivo electronico 1.1",

    'summary': """
        Ple caja y bancos - Detalle de los movimientos del efectivo electronico 1.1""",

    'description': """
        Ple caja y bancos - Detalle de los movimientos del efectivo electronico 1.1
    """,

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    'category': 'Accountig',
    'version': '17.20230124',
    'depends': ['l10n_pe_ple',
                'l10n_latam_invoice_document',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/report_ple_1_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
