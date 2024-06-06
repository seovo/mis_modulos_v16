# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Paymentez Nuvei Payment Provider',
    'version': '2.0',
    'category': 'Accounting/Payment Providers',
    "summary": "Pagos en línea con Nuvei",
    'author': 'PERFEKTESG CIA. LTDA.',
    'maintainer': 'PERFEKTESG CIA. LTDA.',
    'website': 'http://www.luft.la',
    'description': '''Payment Provider: Nuvei Implementation''',
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'USD',
    'depends': [
        'payment',
        'sale',
        'website_payment',
        'website_sale',
    ],
    'data': [
        # 'views/js_files_link.xml',
        'views/payment_provider_views.xml',
        'views/payment_nuvei_templates.xml',
        # 'views/sale_order.xml',
        'views/payment_transaction_view.xml',
        'data/payment_provider_data.xml',
        'data/mail_data.xml',
    ],
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_nuvei/static/src/js/payment.js',
        ],
    },
    "support": "soporte@luft.la",
}
