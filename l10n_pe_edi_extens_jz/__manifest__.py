# -*- coding: utf-8 -*-
{
    "name": "Facturación electrónica para Perú",
    "summary": "Facturación electrónica para Perú",
    "description": """Facturación electrónica para Perú""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "1.1",
    "depends": ["l10n_pe_edi"],
    "data": [
        "views/account_move.xml",
        "views/cron.xml",
    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": False,
    "installable": True,
    "auto_install": False,

}
