{
    'name': 'Desarrollo Florista',
    'version': '17.0',
    'category': 'web',
    "summary": "Desarrollo Florista",
    'author': 'JZOLUTIONS',
    'maintainer': 'JZOLUTIONS',
    'website': 'www.jzolutions.com',
    'description': '''Desarrollo Florista''',
    'license': 'OPL-1',
    'price': 200.00,
    'currency': 'USD',
    'depends': [
        'payment_mercadopago_link_jz',
        #'website_customer_order_delivery_date',

    ],
    'data': [

        'views/templates.xml',
        'views/product_attribute.xml',
        #'views/payment_nuvei_templates.xml',
        'views/sale_order.xml',
        #'views/payment_transaction_view.xml',

        #'data/mail_data.xml',
    ],
    'application': False,

    #'assets': {
    #    'web.assets_frontend': [
    #        'payment_nuvei/static/src/js/payment.js',
    #    ],
    #},
    "support": "jzolution@gmail.com",
}
