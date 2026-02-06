# -*- coding: utf-8 -*-

{
	'name': 'Peru - Multi Journal POS',
	'summary': """Point Of Sale""",
	'version': '17.20240607',
	'description': """Este modulo permite seleccionar diferentes diarios de ventas en el punto de venta""",
	'author': "Oxe360",
	'website': 'http://www.oxe360.com',
	'license': "OPL-1",
	'company': 'Oxe360',
	'category': 'Point of Sale',
	'depends': ['base', 'point_of_sale', 'l10n_pe_edi'],
	'images': ['static/description/icon.png'],
	"data": [
		"views/pos_config_views.xml",
		"views/account_journal_view.xml",
	],
	'assets': {
		"point_of_sale._assets_pos": [
			"pos_multi_journal/static/src/**/*"],
	},
	"installable": True,
	
}
