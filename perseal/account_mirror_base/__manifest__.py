# -*- coding: utf-8 -*-
{
    'name': "Account Mirror Base",

    'description': """Servirá para implementar una aplicación que permita la distribución porcentual de las
    cuentas contables de destino a través del uso de la distribución a otras cuentas""",

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': "17.20250407",

    # any module necessary for this one to work correctly
    'depends': ['account',
                'account_accountant',
                'account_asset'],

    # always loaded
    'data': [
    ],

}
