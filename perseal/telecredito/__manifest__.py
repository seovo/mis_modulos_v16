# -*- coding: utf-8 -*-
{
    'name': "Teletransfer",
    'description': "Teletransfer",
    'author': 'Oxe360',
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",
    'category': 'Localization',
    'version': "17.20230124",
    'depends': [
        'l10n_pe_edi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_menuitem.xml',
        'wizard/teletransfer_views.xml',
        'views/res_partner_bank_views.xml',
    ],
    'installable': False,
}