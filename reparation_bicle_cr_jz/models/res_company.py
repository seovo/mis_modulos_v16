from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    whatsapp_sale_msg_format = fields.Text(string="Formato Whatsapp")