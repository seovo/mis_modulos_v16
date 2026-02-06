# -*- coding: utf-8 -*-

{
	'name': 'Peru - Consulta RUC POS',
	'summary': """Point Of Sale""",
	'version': '17.20250206',
	'description': """Point Of Sale""",
	'author': "Oxe360",
	'website': 'http://www.oxe360.com',
	'license': "OPL-1",
	'company': 'Oxe360',
	'category': 'Point of Sale',
	'depends': ['base', 'point_of_sale', 'l10n_pe_edi' , 'l10n_pe_pos','web'],
	'images': ['static/description/icon.png'],
	"data": [
		"security/pos_security.xml",
		"security/ir.model.access.csv",
		"views/pos_order_views.xml",
	],
	'assets': {
		'point_of_sale._assets_pos': [
			'pos_ruc_query/static/src/**/*',
		],

	},
	"installable": True,
	
}
