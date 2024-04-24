from odoo import api, fields, models , _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    code_l10n_latam_document_type_id = fields.Char(related='l10n_latam_document_type_id.code')