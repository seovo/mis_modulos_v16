# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Display the Product Image on the Sales Order Portal',
    'version': '1.1.1',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category' : 'Sales/Sales',
    'summary': """Portal for Displaying Product Images""",
    'description': """
Portal for Displaying Product Images
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'depends': [
        'sale'
    ],
    'data':[
        'views/sale_portal_templates.xml',
    ],
    'installable' : True,
    'application' : False,
}


