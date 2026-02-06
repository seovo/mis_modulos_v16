
{
    'name':
        "Peru - Libro Permante valorizado 13.1",
    'summary': """
        Ple Permante valorizado 13.1""",
    'description': """
            Ple de compras simplificado electronico 8.3
        """,
    'author': "Oxe360",
    'license': "OPL-1",
    'website': "http://www.oxe360.com",
    "version": "17.20230124",
    "category": "Accounting / Reports",
    'depends': ['account',
                'sale',
                'purchase',
                'stock',

                'sale_management',
                'product_unspsc',
                'l10n_pe_edi',
                'l10n_pe_ple',
                'report_xlsx'],
    'data': [
        # 'data/sequence.xml',
        'security/ir.model.access.csv',
        # 'views/product_template.xml',
        # 'views/kardex_electronico.xml',
        # 'views/config_cost.xml',
        # 'views/menu_item.xml',
        # 'views/stock_picking.xml'
       ],
    "application": False,
    'installable': True,
}
