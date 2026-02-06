# -*- coding: utf-8 -*-
{
    'name': "Peru - Tipo de cambio SBS",
    'description': """Peru - Tipo de cambio SBS""",
    'author': "Oxe360",
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    "category": "Financial Management/Configuration",
    'version': "17.20250114",
    "depends": ["currency_rate_live"],
    "external_dependencies": {
        "python": ["bs4"]
    },
    'images': ['static/description/icon.png'],
    'data': ['data/service_cron_data.xml'],
    # 'post_init_hook': 'update_res_currency_provider',
    'installable': True,
}
