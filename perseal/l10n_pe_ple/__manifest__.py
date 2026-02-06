# -*- coding: utf-8 -*-

{
    'name': "Peru - Electronic Books Program (PLE)",

    'summary': """
        Electronic Books Program""",

    'description': """    """,

    'author': "Oxe360",
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '17.20230124',
    # any module necessary for this one to work correctly
    'depends': ['l10n_pe_edi',
                'report_xlsx',
               ],
    # always loaded

    'data': [
        'security/ir.model.access.csv',
        # 'views/ple_view.xml',
        # 'views/account_move.xml',
        # 'views/res_country.xml',
        # 'data/type_document.xml',
        # 'data/catalog.table.csv',
        # 'data/catalog_element.csv',
        # 'data/account.tax.csv',
        # 'data/ple.configuration.csv',
        # # consolidated views
        # 'security/res.groups.xml',
        # 'views/ple_configuration.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
}
