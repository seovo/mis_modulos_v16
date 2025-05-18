from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    whatsapp_sale_msg_format = fields.Text(string="Formato Whatsapp")
    whatsapp_template_id = fields.Many2one('mail.template')