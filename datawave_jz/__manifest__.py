# -*- coding: utf-8 -*-
{
    "name": "DataWave Firesolutions",
    "summary": "DataWave Firesolutions",
    "description": """
        DataWave Firesolutions
    """,
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["base"],
    "data": [
         "security/ir.model.access.csv",
         "data/cron.xml",
         "views/total_nine_box.xml",
         "views/total_nine_box_mc.xml",
         "views/total_nine_box_per_store.xml",
         "views/total_nine_box_per_store_mc.xml",

    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal","pymssql","pandas"]},
    "application": False,
    "installable": True,
    "auto_install": False,

}
