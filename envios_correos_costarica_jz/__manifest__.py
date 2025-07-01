{
    'name': 'Envios Correos Costa Rica',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    "summary": "Envios Correos Costa Rica",
    'author': 'JZOLUTIONS',
    'maintainer': 'JZOLUTIONS',
    'website': 'www.jzolutions.com',
    'description': '''Envios Correos Costa Rica''',
    'license': 'OPL-1',
    'price': 200.00,
    'currency': 'USD',
    'depends': [
        'payment',
        'sale',
        'website_payment',
        'website_sale',
        'delivery',
        'sale_stock',
        'website_in_store_pickup',
        'l10n_cr_identification_type'
    ],
    'data': [
        #'data/payment_templates.xml',
        'views/delivery_carrier.xml',
        'views/template.xml',
        #'views/payment_nuvei_templates.xml',
        'views/sale_order_view.xml',
        #'views/payment_transaction_view.xml',
        #'data/payment_provider_data.xml',
        #'data/mail_data.xml',
    ],
    'application': False,
    #'post_init_hook': 'post_init_hook',
    #'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'envios_correos_costarica_jz/static/src/js/address_form.js',
        ],


    },


    #"support": "jzolution@gmail.com",
}
