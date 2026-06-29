# -*- coding: utf-8 -*-
{
    'name': "EVENTOS PROCIENCIA",
    'summary': """EVENTOS PROCIENCIA""",

    'description': """EVENTOS PROCIENCIA""",
    'author': "Jzolutions",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['sale_management','crm','stock','purchase_in_sale_jz'],
    #,'planning'

    # always loaded
    'data': [
        #"security/group.xml",
        "security/ir.model.access.csv",
        'views/sale_order.xml',
        'views/portal_templates.xml',
        'views/crm_lead.xml',
        'views/product.xml',
        'views/planning_role.xml',
        'views/stock_picking_type.xml',
        #'views/report_invoice.xml'
    ],

   'assets': {

        'web.assets_frontend': [
            'eventos_prociencia_jz/static/src/js/portal.js',

        ],

    },


}