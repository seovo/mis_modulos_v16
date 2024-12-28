# -*- coding: utf-8 -*-
{
    'name': 'Compare Price On Product Variants',
    "author": "Jzolutions",
    'version': '17.0',
    #'live_test_url': "https://youtu.be/Z3ZJjF7_DyM",
    #"images":['static/description/main_screenshot.png'],
    'summary': "Compare Price On Product Variants",
    'description': """Compare Price On Product Variants""",
    "license" : "OPL-1",
    'depends': ['base','website','product','sale','sale_management','website_sale'],
    'data': [
            'views/product_variants_view.xml',
            #'views/product_templates.xml',
            ],
    'installable': True,
    'auto_install': False,
    #'price': 15,
    #'currency': "EUR",
    'category': 'Sale',

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: