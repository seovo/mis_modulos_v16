# -*- coding: utf-8 -*-
{
    'name': "Peru - Libro de ventas electronico 14.1",

    'summary': """
        Ple de ventas 14.1""",

    'description': """
        Ple de ventas 14.1
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
        # 'views/report_ple_14_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
