from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    show_code_invoice = fields.Boolean(string='Show Code Invoice', default=False)


# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     show_code_invoice = fields.Boolean(string='No Show Code Invoice', related='company_id.show_code_invoice', readonly=False)