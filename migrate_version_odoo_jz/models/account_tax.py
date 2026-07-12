from odoo import api, fields, models , _

class AccountTax(models.Model):
    _inherit = "account.tax"
    tax_migration_jz_ids = fields.One2many('tax.migration.jz','tax_id')