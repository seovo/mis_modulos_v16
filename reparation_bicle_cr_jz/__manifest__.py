# -*- coding: utf-8 -*-
{
    "name": "Reparación Bicicletas",
    "summary": "Reparación Bicicletas",
    "description": """Reparación Bicicletas""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["sale_management","whatsapp_api_evolution_jz"],
    "data": [
        "security/ir.model.access.csv",
        'views/sale_order.xml',
        'views/view_company_form.xml',
        #'views/menu.xml',
        #'views/report.xml',

    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": True,
    "installable": True,
    "auto_install": False,

}
