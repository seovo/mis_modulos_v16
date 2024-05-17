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






