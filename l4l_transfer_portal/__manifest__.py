# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

{
    'name': "Delivery / Shipment Portal",
    'category': 'Inventory/Inventory',
    'version': '17.0.1.0',
    'sequence': 1,
    'summary': """Transfer Details, Transfer Portal, Delivery Portal, Shipment Portal,  Reciept Portal, Short By, Search By, Filter By, Search Functionality, Website, Sale Order, Order, Purchase, Invoice, Bill, Receipt, Vendor, Partner, Contact, Transfer, Inventory, Shipment, Picking Portal, Picking, Portal, Delivery""",
    'description': """This App Allows Your Customers and Vendors to Print Delivery Slips From The Portal of Your Website to My Account and also Filter, Group or Search Delivery or Shipment.""",
    'author': 'Leap4Logic Solutions Private Limited',
    'website': 'https://leap4logic.com/',
    'depends': ['mail', 'contacts', 'website', 'portal', 'stock'],
    'data': [
        'views/transfer_portal_template_views.xml',
        'security/ir.model.access.csv',
        'views/stock.picking.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': ['static/description/banner.gif'],
    'price': '22.99',
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/SRxyqEIzs7A',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
