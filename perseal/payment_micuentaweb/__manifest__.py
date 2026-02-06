# coding: utf-8
#
# Copyright © Lyra Network.
# This file is part of Izipay plugin for Odoo. See COPYING.md for license details.
#
# Author:    Lyra Network (https://www.lyra.com)
# Copyright: Copyright © Lyra Network
# License:   http://www.gnu.org/licenses/agpl.html GNU Affero General Public License (AGPL v3)

{
    'name': 'Izipay Payment Provider',
    'version': '3.0.3',
    'summary': 'Accept payments with Izipay secure payment gateway.',
    'category': 'Accounting/Payment Providers',
    'author': 'Lyra Network',
    'website': 'https://www.lyra.com/',
    'license': 'AGPL-3',
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_micuentaweb_templates.xml',
        # 'data/payment_icon_data.xml',
        'data/payment_provider_data.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True
}
