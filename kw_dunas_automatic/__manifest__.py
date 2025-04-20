# -*- coding: utf-8 -*-
{
    "name": "kw_dunas_automatic",
    "summary": "kw_dunas_automatic",
    "description": """kw_dunas_automatic""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "1.1",
    "depends": ["sale_management","stock",
                "l10n_latam_invoice_document",
                "stock_picking_batch_extended",
                "custom_stock_picking_batch"],
    "data": [
        'views/sale_order.xml',
        'views/stock_picking_batch.xml'


    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": False,
    "installable": True,
    "auto_install": False,

}
