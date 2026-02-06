# -*- coding: utf-8 -*-

{
	'name': 'Peru - Point of Sale - Defaults',
	'summary': """Point Of Sale""",
	'version': '17.20250212',
	'description': """este modulo permite establer un clinte por defecto en el punto de venta""",
	'author': "Oxe360",
	'website': 'http://www.oxe360.com',
	'license': "OPL-1",
	'company': 'Oxe360',
	'category': 'Point of Sale',
	'depends': ['base', 'point_of_sale', 'l10n_pe_edi', 'l10n_pe_pos'],
	'images': ['static/description/icon.jpg'],
	"data": ['views/pos_config_view.xml'],
	# "assets": {
    #     "point_of_sale._assets_pos": ["pos_defaults/static/src/**/*"],
    # },
	"installable": True,
	
}
