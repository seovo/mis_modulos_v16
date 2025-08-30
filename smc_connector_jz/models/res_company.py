from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    smc_category_ids = fields.Many2many('product.category')
    smc_excluded_partner_ids = fields.Many2many('res.partner','smc_excluded_partner_ids')
    smc_usuario = fields.Char()
    smc_password = fields.Char()
    smc_dt = fields.Char()
    smc_name_dt = fields.Char()
