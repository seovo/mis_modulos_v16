# -*- coding: utf-8 -*-
{
    'name': 'Invoice Global Discount',
    'version': "17.20230508",
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    'summary': 'Invoice Global Discount',
    'description': "Invoice Global Discount",

    'depends': ['l10n_pe_edi',
                'product',
                'pos_loyalty'],
    'category': 'Accounting/Accounting',
    'data': [
             'views/product_view.xml',
    ],
}