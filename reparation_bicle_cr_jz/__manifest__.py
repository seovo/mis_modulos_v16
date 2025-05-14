# -*- coding: utf-8 -*-
{
    "name": "Reparación Bicicletas",
    "summary": "Reparación Bicicletas",
    "description": """Reparación Bicicletas""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["repair"],
    "data": [
        "security/ir.model.access.csv",
        'views/sale_order.xml',
        #'views/line_repair_order.xml'

    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": True,
    "installable": True,
    "auto_install": False,

}
