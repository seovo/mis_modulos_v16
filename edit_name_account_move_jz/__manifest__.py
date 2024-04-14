# -*- coding: utf-8 -*-
{
    "name": "Edit Name Account Move",
    "summary": "Edit Name Account Move",
    "description": """Edit Name Account Move""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "1.1",
    "depends": ["account","l10n_latam_invoice_document"],
    "data": [
        "security/group.xml",
        "views/account_move.xml",
    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": False,
    "installable": True,
    "auto_install": False,

}
