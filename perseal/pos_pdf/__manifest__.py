# -*- coding: utf-8 -*-

{
	'name': 'Peru - Reporte POS',
	'summary': """Point Of Sale""",
	'version': '17.20250205',
	'description': """Point Of Sale""",
	'author': "Oxe360",
	'website': 'http://www.oxe360.com',
	'license': "OPL-1",
	'company': 'Oxe360',
	'category': 'Point of Sale',
	'depends': ['base', 'point_of_sale', 'l10n_pe_edi'],
	'images': ['static/description/icon.png'],
	"data": [
		"views/pos_config_views.xml",
	],
	'assets': {
		'point_of_sale._assets_pos': [
			'pos_pdf/static/src/**/*',
		],

	},
	"installable": True,
	
}
