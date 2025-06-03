from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        if len(self) == 1:
            if self.l10n_pe_edi_operation_type == '1001'  :
                note = self.narration
                self.narration = None

        res = super().action_post()

        if len(self) == 1:
            if self.l10n_pe_edi_operation_type == '1001'  :
                self.narration = note


        return  res


    def button_process_edi_web_services(self):
        if len(self) == 1:
            if self.l10n_pe_edi_operation_type == '1001'  :
                note = self.narration
                self.narration = None

        res = super().button_process_edi_web_services()


        if len(self) == 1:
            if self.l10n_pe_edi_operation_type == '1001'  :
                self.narration = note


        return  res