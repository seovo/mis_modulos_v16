# -*- coding: utf-8 -*-
{
    "name": "REPORT LINEAS DE VENTAS",
    "summary": """REPORT LINEAS DE VENTAS""",
    "description": """REPORT LINEAS DE VENTAS""",
    "author": "JZOLUTIONS",

    "category": "Uncategorized",
    "version": "0.1",
    "depends": [
        "sale_purchase",

    ],
    # always loaded
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_line.xml',
        'views/sale_report_sensotek.xml',
    ],
    # 'images': ['static/description/odoo-woo.gif'],
}
