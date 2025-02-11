from odoo import api, fields, models , _


class AccountPaymentRegister(models.TransientModel):
    _inherit =  'account.payment.register'

    def action_create_payments(self):



        #raise ValueError(self.line_ids.move_id)
        res = super().action_create_payments()

        if self.partner_bank_id.bank_id:
            move = self.line_ids.move_id

            self.env['bank.origin'].create({
                'move_id': move.id,
                'date': self.payment_date,
                'operation_number': self.communication,
                'bank_id': self.partner_bank_id.bank_id.id
            })

        move.get_narration_dx()

        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    journal_id = fields.Many2one('account.journal',
                                 string="Diario",
                                 #required=True ,
                                 domain=[('code_l10n_latam_document_type_id','in',['01','03'])])

    sale_line_id = fields.Many2one('sale.order.line',string="Especificar Pago")

    '''

    def create_invoices(self):
        for sale in self.sale_order_ids:
            #sale.journal_id = self.journal_id.id
            if self.sale_line_id:
                sale.sale_line_payment_id = self.sale_line_id.id
        res = super().create_invoices()
        for sale in self.sale_order_ids:
            sale.journal_id = None
            sale.sale_line_payment_id = None
            for line in sale.order_line:
                if line.amount_initial_desc > 0:
                    if line.price_unit != line.amount_initial_desc :
                        line.write({
                            'price_unit': line.amount_initial_desc
                        })
                        #line.price_unit =


        return res
        
    '''


