# -*- coding: utf-8 -*-
{
    'name': 'Perú - Agent retention',
    'version': "17.20230124",
    'author': "Oxe360",
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",
    'summary': 'Agent retention',
    'description': "Agente retencion",
    'depends': [
        'l10n_pe_agent_retention_pdf',
        'l10n_pe_credit_payments_pdf',
    ],
    'category': 'Hidden',
    'data': [
        'views/report_invoice.xml',
    ],
    'auto_install': False,
    'installable': True,
}
