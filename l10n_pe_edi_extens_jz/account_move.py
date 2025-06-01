from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'
    def button_process_edi_web_services(self):
        note = self.note
        self.note = None
        res = super().button_process_edi_web_services()
        self.note = note


        return  res