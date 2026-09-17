{
    'name': 'Phone Call Crm',
    'author': 'Nians',
    'website': 'https://nians.com/odoo',
    'support': 'support@technians.com',
    'version': '19.0.1.0.0',
    'category': 'CRM',
    'summary': 'Calls Feature & Auto-format phone number & CRM',
    'description': """Added Similar Calls Feature & Auto-format phone number and show the phone calls in crm""",
    'depends': ['base', 'crm', 'ts_phone_calls'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_lead_wizard.xml',
        'views/crm_leads.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}

