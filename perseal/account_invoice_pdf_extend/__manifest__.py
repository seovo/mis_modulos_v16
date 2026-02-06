# -*- coding: utf-8 -*-
{
    'name': 'Peru - Reporte CPE Extend',
    'version': '17.20230925',
    'website': 'http://www.oxe360.com',
    'category': 'Localization',
    'description': u"""
    No mostrar el codigo de productos en las lineas de factura
    """,
    'author': 'Oxe360',
	'company': 'Oxe360',
    'depends': [
        'account_invoice_pdf',],
    'images': ['static/description/icon.jpg'],
    'data': [],
    'application': False,
    'license': 'OPL-1',
    'pre_init_hook': '_post_install',
    'uninstall_hook': '_uninstall_hook'
}