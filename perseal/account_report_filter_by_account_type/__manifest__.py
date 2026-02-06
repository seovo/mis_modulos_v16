# -*- coding: utf-8 -*-
{
    'name': 'Account report extend',
    'summary': """""",
    'description': """""",
    'author': "Oxe360",
    'website': 'http://www.osse.com.pe',
    'license': "OPL-1",
    'category': 'Localization',
    'version': "17.20250307",
    'depends': [
        'web',
        'account_accountant',
        'account_reports'
    ],
    'data': [
        # 'views/search_template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_report_filter_by_account_type/static/src/**/*.js',
            'account_report_filter_by_account_type/static/src/**/*.xml',
        ],
    },
    'installable': True,
}