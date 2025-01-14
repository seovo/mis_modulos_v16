from odoo import api, fields, models , _

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    code_l10n_latam_document_type_id = fields.Char(related='l10n_latam_document_type_id.code')
    journal_reverse_jz = fields.Many2one('account.journal', string='Diario Reversa x Defecto')

    def action_import_transaction_villasur(self):
        return {
            "name": f"Importar Masivo {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            # "view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "import.bancarios.vill",
            # "res_id": self.id,
            "target": "new",
            #"domain": [('team_id', '=', self.id)],
            "context": {
                'default_journal_id': self.id,
                #'search_default_group_user_id': 1
            }

        }