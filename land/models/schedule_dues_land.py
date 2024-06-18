from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class ScheduleDuesLand(models.Model):
    _name          = 'schedule.dues.land'
    _description   = 'schedule.dues.land'
    number_due     = fields.Integer(string="Cuota")
    date           = fields.Date(string="Fecha")
    balan          = fields.Float(string="Balance")
    amount         = fields.Float(string="Mensualidad")
    note           = fields.Text(string="Nota")
    is_paid        = fields.Boolean(string="Pagado?")
    order_id       = fields.Many2one('sale.order')
    move_id        = fields.Many2one('account.move',string="Factura")
    invoice_date   = fields.Date(related='move_id.invoice_date',string="Fecha Pagada")
    amount_due_land = fields.Float(related='move_id.amount_due_land',string="Monto Pagado")
    amount_mora_land = fields.Float(related='move_id.amount_mora_land',string="Mora")

    def invoice_here_land(self):

        #if not self.order_id.journal_id:
        #    raise ValidationError('INDIQUE UN DIARIO')

        numer_due = self.number_due
        sale = self.order_id

        for invc in self.order_id.invoice_ids:
            if invc.amount_total == self.order_id.price_initial_land:
                #invc.invoice_date = self.order_id.date_sign_land
                invc.get_is_initial_land()

        invoice_idsx = self.order_id.invoice_ids
        invoice_ids = []

        for inv in invoice_idsx:
            if inv.is_initial_land :
                continue
            invoice_ids.append(inv.id)


        invoices = self.order_id.env['account.move'].search([
            ('id', 'in', invoice_ids),
            ('is_initial_land','!=',True)
        ], order='invoice_date asc')

        len_invoices = len(invoices)

        diff_invoices = numer_due - len_invoices

        if diff_invoices > 0:
            for i in range(diff_invoices):
                dx = {
                    'advance_payment_method': 'delivered',
                    'sale_order_ids': [(6, 0, [sale.id])],
                    'journal_id':  self.order_id.journal_id.id  if   self.order_id.journal_id.id else 10

                }
                wizard = self.env['sale.advance.payment.inv'].create(dx)
                wizard.create_invoices()

        self.order_id.update_dates_land()

        for invoice in self.order_id.invoice_ids:
            if invoice.state == 'draft':
                invoice.action_post()

        self.order_id.update_schedule()

        self.order_id.journal_id = None









