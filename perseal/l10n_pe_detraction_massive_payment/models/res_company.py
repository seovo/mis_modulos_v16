from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    detraction_account_id = fields.Many2one('account.account', string='Cuenta de detraccion')