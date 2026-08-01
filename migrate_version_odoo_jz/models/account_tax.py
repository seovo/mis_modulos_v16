from odoo import api, fields, models , _

class AccountGroup(models.Model):
    _inherit = "account.group"
    account_group_migration_jz_ids  = fields.One2many('account.group.migration.jz','account_group_id')

class AccountTax(models.Model):
    _inherit = "account.tax.group"
    tax_group_migration_jz_ids  = fields.One2many('tax.group.migration.jz','tax_group_id')

class AccountTax(models.Model):
    _inherit = "account.tax"
    tax_migration_jz_ids = fields.One2many('tax.migration.jz','tax_id')

class AccountJournal(models.Model):
    _inherit = "account.journal"
    tax_migration_jz_ids = fields.One2many('journal.migration.jz','journal_id')