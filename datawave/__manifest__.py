# -*- coding: utf-8 -*-
{
    'name': "Datawave",

    'summary': """
        Módulo para gestionar productos de Datawave.""",

    'description': """
        Este módulo permite la gestión de productos, incluyendo SKU, nombre, categoría, unidad de medida y estado.
    """,

    'author': "Jules",
    'website': "http://www.yourappi.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base'],

    'data': [
        "security/ir.model.access.csv",
        "views/input_cliente.xml",
        "views/inputs_transaccional.xml",
        "views/input_others.xml",
        "views/intermedios.xml",
        "views/output.xml",
        "views/config_tablas.xml",
        "views/menus.xml",
        "views/res_config_settings_views.xml"
    ],
    'demo': [],
}
