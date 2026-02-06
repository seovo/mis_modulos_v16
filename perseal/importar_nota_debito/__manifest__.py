# -*- coding: utf-8 -*-
{
    'name': "Importar nota de débito",
    'summary': "Importar nota de débito",
    'description': "Importar nota de débito",
    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",
    'category': 'Accountig',
    'version': '17.20230825',
    'depends': [
        'account',
        'sale',
        'l10n_latam_invoice_document',
        'l10n_pe_edi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_views.xml',
        'wizard/carga_nota_debito_views.xml',
    ],
}
