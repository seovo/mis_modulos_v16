# -*- coding: utf-8 -*-
{
    'name': "Account Tag Mirror",

    'description': """Servirá para implementar una aplicación que permita la distribución porcentual de las
    cuentas contables de destino a través del uso de la distribución a otras cuentas""",

    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': "17.20240419",

    # any module necessary for this one to work correctly
    'depends': ['account_mirror_base'],

    # always loaded
    'data': ['views/account_account_view.xml'],
    'installable': True,
}