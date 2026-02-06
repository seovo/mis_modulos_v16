# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de ventas simplificado electronico 14.2",

    'summary': """
        Ple de ventas simplificado electronico 14.2""",

    'description': """
        Ple de ventas simplificado electronico 14.2
    """,

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    'category': 'Accountig',
    'version': '17.20230124',
    'depends': ['l10n_pe_ple'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/report_ple_14_2_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': False,
}
