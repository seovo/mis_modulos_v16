# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Website Repair Portal',
    'version': '17.0.1.1',
    'sequence': 1,
    'category': 'Website',
    'description':
        """
        This Module help to Portal can use Repair request

-Portal User can access their Repair Orders
Portal User can download Repair Order PDF report from the Website


Website Repair Portal
Odoo app to access repair request website Portal,Website repair Portal, repair request,repair Portal

    """,
    'summary': 'Odoo app to access repair request website Portal,Website repair Portal, repair request,repair Portal,Repair Orders, repair pds reports, repair website, repair portal website',
    'depends': ['portal','web_editor','repair','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_order_portal_templates.xml'
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':29.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
