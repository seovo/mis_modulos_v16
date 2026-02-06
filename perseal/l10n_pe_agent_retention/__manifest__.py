# -*- coding: utf-8 -*-
{
    'name': 'Perú - Agent retention',
    'version': "17.20250228",
    'author': "Oxe360",
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",
    'summary': 'Agent retention',
    'description': "Agente retencion",
    'depends': [
        'l10n_pe_edi',
    ],
    'category': 'Accounting/Accounting',
    'data': [
        'views/res_partner_views.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
}
