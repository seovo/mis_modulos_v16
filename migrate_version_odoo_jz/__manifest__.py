# -*- coding: utf-8 -*-
{
    "name": "Migrador de Versiones de Odoo",
    "summary": "Migrador de Versiones de Odoo",
    "description": """Migrador de Versiones de Odoo""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["sale_management","l10n_pe_edi_odoofact",'land'],
    "data": [
        'security/ir.model.access.csv',
        'views/migrate_jz.xml'
    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": True,
    "installable": True,
    "auto_install": False,

}
