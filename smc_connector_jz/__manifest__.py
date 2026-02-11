# -*- coding: utf-8 -*-
{
    "name": "Conector SMC Odoo - SOAP",
    "summary": """
        Conector SMC Odoo - SOAP
    """,
    "description": """
        Conector SMC Odoo - SOAP
        
        https://ws.smcmx.com.mx/wssmc_test/index.html
    """,
    "author": "Jzolutions",
    "website": "https://www.jzolutions.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    #"price": 150.00,
    #"currency": "USD",
    # any module necessary for this one to work correctly
    "depends": ["base","account","catalogos_cfdi"],
    # always loaded
    "data": [
        'views/account_move.xml',
        'views/res_company.xml',
        'views/res_partner.xml'

    ],
    "license": "LGPL-3"
    #'images': ['static/description/odoo-mercadolibre.gif'],
}
