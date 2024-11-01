{
    'name': 'ComboPay Payment Provider',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    "summary": "Pagos en línea con Mercado Pago",
    'author': 'JZOLUTIONS',
    'maintainer': 'JZOLUTIONS',
    'website': 'www.jzolutions.com',
    'description': '''Payment Provider: Mercado Pago''',
    'license': 'OPL-1',
    'price': 200.00,
    'currency': 'USD',
    'depends': [
        'payment',
        'sale',
        'website_payment',
        'website_sale',
    ],
    'data': [
        'data/payment_templates.xml',
        'data/payment_provider_data.xml',
        # 'views/js_files_link.xml',
        #'views/payment_provider_views.xml',
        #'views/payment_nuvei_templates.xml',
        # 'views/sale_order.xml',
        #'views/payment_transaction_view.xml',

        #'data/mail_data.xml',
    ],
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    #'assets': {
    #    'web.assets_frontend': [
    #        'payment_nuvei/static/src/js/payment.js',
    #    ],
    #},
    "support": "jzolution@gmail.com",
}
