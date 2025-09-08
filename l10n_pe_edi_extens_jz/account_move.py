from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_date')
    def change_date_jz_jz(self):
        for record in self:
            if record.invoice_date:
                diff = fields.Datetime.now().date() - record.invoice_date

                raise ValueError(diff.date)


    def action_post(self):
        res = super().action_post()
        if len(self) == 1 :
            if self.edi_document_ids:
                self.button_process_edi_web_services()
        return res



    #def action_retry_edi_documents_error(self):
    #    for record in self:
    #        record.edi_document_ids.unlink()
    #        record.button_process_edi_web_services()




    def button_process_edi_web_services(self):
        if len(self) == 1:
            note = self.narration
            self.narration = None


        res = super().button_process_edi_web_services()

        #if self.l10n_pe_edi_operation_type == '1001':
        if len(self) == 1:
            self.narration = note



        return  res
