from odoo import api, fields, models , _

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    journal_id = fields.Many2one('account.journal',
                                 string="Diario",
                                 required=True ,
                                 domain=[('code_l10n_latam_document_type_id','in',['01','03'])])

    def create_invoices(self):
        for sale in self.sale_order_ids:
            sale.journal_id = self.journal_id.id
        res = super().create_invoices()
        for sale in self.sale_order_ids:
            sale.journal_id = None
        return res


