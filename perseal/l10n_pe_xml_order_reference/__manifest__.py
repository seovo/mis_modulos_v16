# -*- coding: utf-8 -*-
{
    'name': 'Referencia de orden en la factura',
    'version': "17.20250428",
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    'summary': 'Order reference in Invoice',
    'description': "Order reference in Invoice",

    'depends': ['l10n_pe_edi',
                'account_edi_ubl_cii'],

    'category': 'Accounting/Accounting',
    'data': [
             'views/res_partner_view.xml',
             'views/account_move_view.xml'
    ],
}