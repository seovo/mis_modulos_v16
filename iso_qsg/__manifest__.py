# -*- coding: utf-8 -*-
{   "name": "ISO QSG",
    "summary": """ISO QSG""",
    "description": """ISO QSG""",
    "author": "JZolutions",
    "category": "Uncategorized",
    "version": "1.0",
    "license": "OPL-1",
    "depends": [
        "multiversion_iso_qsg",
        #"stock",
        #"website_sale",
        #"contacts",
        #"sale_management",

    ],
    # always loaded
    "data": [
        'views/process_qsg.xml',
        'views/control_operation_qsg.xml',
        'views/ro_qsg.xml',
        'views/monitoring_qsg.xml',
        'views/action_qsg.xml',
        'views/menu.xml'

    ],
    # 'images': ['static/description/odoo-woo.gif'],
}
