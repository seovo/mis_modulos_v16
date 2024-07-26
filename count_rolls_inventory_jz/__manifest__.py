# -*- coding: utf-8 -*-
{
    "name": "Count Rolls Inventory",
    "summary": "Count Rolls Inventory",
    "description": """
        Count Rolls Inventory
    """,
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        'views/stock_quant.xml',
        'views/purchase.xml',
        'views/sale_order.xml',
        'views/wizard.xml',
        'views/product_template_attribute_value.xml'

    ],
    "application": False,
    "installable": True,
    "auto_install": False,


}
