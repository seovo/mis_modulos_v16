# -*- coding: utf-8 -*-
{
    "name": "List PowerBi Report",
    "summary": "List PowerBi Report",
    "description": """
        List PowerBi Report
    """,
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "1.1",
    "depends": ["base"],
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/list_powerbi.xml",
        "views/template.xml",
    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": False,
    "installable": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            #'https://code.jquery.com/jquery-3.5.1.min.js',
            #'https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.min.js',
            #'https://cdnjs.cloudflare.com/ajax/libs/powerbi-client/2.15.1/powerbi.min.js',
            #"list_powerbi_report/static/src/js/powerbi.min.js",
            #"list_powerbi_report/static/src/js/index.js",
            #"citix_shared/static/src/xml/*.xml",
            #"citix_shared/static/src/css/*.css",
        ]
    },
}
