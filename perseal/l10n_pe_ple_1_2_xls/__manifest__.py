# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de caja y bancos - Detalle de los movimientos de la cuenta corriente fisico 1.2",
    'summary': """
        Ple caja y bancos - Detalle de los movimientos de la cuenta corriente fisico 1.2""",

    'description': """
        Ple caja y bancos - Detalle de los movimientos de la cuenta corriente fisico 1.2
    """,

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    'category': 'Accountig',
    'version': '17.20230124',
    'depends': ['l10n_pe_ple',
                'l10n_latam_invoice_document',
                'l10n_pe_ple_1_2',
                'report_xlsx'
                ],
    # always loaded
    'data': [
        # 'views/report_ple_1_2_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
