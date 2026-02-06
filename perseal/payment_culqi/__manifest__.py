# -*- coding: utf-8 -*-

{
    'name': 'Culqi Payment Acquirer',
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: Culqi Implementation',
    'version': '17.20230124',
    'license': "OPL-1",
    'description': """Culqi Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_culqi_templates.xml',
        'views/res_partner.xml',
        'views/culqi.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'images': ['static/description/icon.png'],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'installable': False,
}
