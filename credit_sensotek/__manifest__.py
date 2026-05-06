# -*- coding: utf-8 -*-
{
    "name": "Credit Sensotek",
    "summary": """
        Credit Sensotek
    """,
    "description": """Credit Sensotek""",
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
    "depends": ["sale_management"],
    # always loaded
    "data": [
        'security/group.xml'
    ],
    "license": "LGPL-3"
    #'images': ['static/description/odoo-mercadolibre.gif'],
}
