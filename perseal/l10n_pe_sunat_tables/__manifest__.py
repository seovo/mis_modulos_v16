# -*- coding: utf-8 -*-

{
    'name': "Peru - Tablas sunat",

    'summary': """
        Tablas sunat""",

    'description': """ Tablas sunat para generacion de libros e informes    """,

    'author': "Oxe360",
    'website': "http://www.oxe360.com",
    'license': "OPL-1",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '17.20230124',

    # any module necessary for this one to work correctly
    'depends': ['account',
                'l10n_pe',
                'l10n_latam_invoice_document'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/catalog.table.csv',
        'data/catalog.element.csv',
        'data/bank_data.xml',
        'data/l10n_latam_document_type.xml',
        # 'views/account_journal_view.xml',
        # 'views/catalog_table_view.xml',
        # 'views/l10n_latam_document_type_view.xml'
    ],
    'installable': True,
}
