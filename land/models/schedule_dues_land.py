from odoo import api, fields, models , _

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
    move_id        = fields.Many2one('account.move')
    invoice_date   = fields.Date(related='move_id.invoice_date',string="Fecha Pagada")
    amount_due_land = fields.Float(related='move_id.amount_due_land',string="Monto Pagado")
    amount_mora_land = fields.Float(related='move_id.amount_mora_land',string="Mora")






