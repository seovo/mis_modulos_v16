# -*- coding: utf-8 -*-
{
    'name': 'Product Barcode Generator',
    'author': 'Oxe360',
    'website': 'http://www.oxe360.com',
    'version': '17.20230124',
    'category': 'Sales',
    'summary': 'Default Make Barcode Module,New Product Barcode Generate App,Existing Product Barcode Generate Application, Existing Multi Product Barcode Create, Custom Product Barcode Generator Odoo.',
    'description': """
    Currently in odoo barcode number not auto-generated in the product, our module help to the generated barcode for the product. You can also create/update mass product barcodes. you can also choose different barcode types.
 Automatic Generate Product Barcode Odoo
 By Default Make Barcode Module, Auto Generate New Product Barcode, Automatic Generate Existing Product Barcode, Auto Create Existing Multi Product Barcode, Custom Product Barcode Generator Odoo.
 Default Make Barcode Module,New Product Barcode Generate App,Existing Product Barcode Generate Application, Existing Multi Product Barcode Create, Custom Product Barcode Generator Odoo.
""",
    'depends': [
        'product',
        'base_setup'
    ],
    'images': ['static/description/background.jpg', ],
    'data': [
        'security/barcode_generator_group.xml',
        'security/ir.model.access.csv',
        'views/product_barcode_generator.xml',
        'views/product_view.xml',
        'views/res_config_settings_views.xml',
    ],
    "license": "OPL-1",
    'application': True,
    'installable': False,
}
