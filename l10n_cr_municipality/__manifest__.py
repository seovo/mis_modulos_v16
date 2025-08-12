{
    "name": "l10n_cr_municipality",
    "version": "17.0.4.5",
    "author": "Mejorado por: Felipe Montero",
    "website": "https://kibuinc.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "account",
        "l10n_cr_territories",
        "sale",
        "uom",
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        # data
        "data/ir_sequence.xml",
        "data/sequence_preventive.xml",
        "data/product_product.xml",
        #"data/l10n_cr_identification.xml",
        "data/l10n_cr_patent_type.xml",
        "data/l10n_cr.ciiu.csv",
        "data/patent_certificate_paperformat.xml",

        'reports/patent_reports.xml',
        # reports
        "reports/patent_certificate.xml",
        "reports/patent_certificate_licor.xml",
        "reports/patent_pos.xml",
        "reports/patent_sign.xml",
        "reports/patent_prevention_report.xml", #Nuevo
        # reports patents

        'reports/patent_deny_licor_template.xml',
        'reports/patent_aprobb_licor_template.xml',
        'reports/patent_aprobb_mcr_template.xml',
        'reports/patent_deny_mcr_template.xml',
        # views
        "views/menus.xml",
        "views/l10n_cr_land.xml",
        "views/l10n_cr_patent_approve_wizard.xml",
        "views/l10n_cr_patent_reject_wizard.xml",
        "views/l10n_cr_patent.xml",
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/invoices_payments_views.xml",

        #wizard
        "wizard/patent_certificate_autorization_wizard.xml",
        "wizard/patent_select_prevention.xml",
        "wizard/patent_change_number.xml", #Nuevo 24-11-21
        'views/patent_report.xml',

    ],
    'application': True,
}
