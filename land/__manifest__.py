# -*- coding: utf-8 -*-
{
    "name": "Land",
    "summary": "Land",
    "description": """ Land""",
    "author": "Jzolutions",
    "category": "Uncategorized",
    "version": "1.1",
    "depends": ["sale_management","l10n_pe_edi_odoofact"],
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/product_attribute_view_form.xml",
        "views/product_template_form_view.xml",
        "views/account_move.xml",
        "views/sale_order.xml",
        "wizard/import_land.xml",

        "views/report_invoice_document.xml",
        'wizard/view_sale_advance_payment_inv.xml',
        "views/seller_land.xml",
        "views/commission_land.xml",
        "views/crm_team_view_form.xml",
        "data/sequence.xml",
        "data/cron.xml",
    ],
    # 'uninstall_hook': 'uninstall_hook',
    #"external_dependencies": {"python": ["msal"]},
    "application": False,
    "installable": True,
    "auto_install": False,

}
