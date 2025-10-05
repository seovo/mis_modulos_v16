# -*- coding: utf-8 -*-
{
    "name": "Multi Almacen Website",
    "summary": "Multi Almacen Website",
    "description": """
        Stock Multi Almacen Website
    """,
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "17.0",
    "depends": ["website_sale"],
    "data": [

        #"security/ir.model.access.csv",
        'views/templates.xml',
        'views/res_currency.xml'
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    'assets': {
        'web.assets_frontend': [
            'multi_currency_website_jz/static/src/js/website_sale.js',
        ],


     },

}
