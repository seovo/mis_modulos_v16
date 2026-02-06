# -*- coding: utf-8 -*-
{
    'name': "Account Analytic Tag Mirror",
    'description': """Este módulo permite distribuir porcentualmente las cuentas contables de destino utilizando cuentas analíticas,
    facilitando una gestión más precisa y flexible de la contabilidad analítica.""",
    'author': 'Oxe360',
    'website': 'http://www.oxe360.com',
    'license': "OPL-1",
    'category': 'Localization',
    'version': "17.20240423",
    # any module necessary for this one to work correctly
    'depends': [
        'analytic',
        'account_mirror_base'],
    # always loaded
    'data': ['views/analytic_account_view.xml'],
    # only loaded in demonstration mode
    'installable': True,
}
