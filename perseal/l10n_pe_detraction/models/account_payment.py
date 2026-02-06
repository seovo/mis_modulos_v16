# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_detraction_pay = fields.Boolean(string='Pago detracción?')
    detraction_operation_number = fields.Char(string='Nro detracción')
    detraction_operation_date = fields.Date(string='Fecha detracción')
    move_detraction_id = fields.Many2one('account.move', string="Documento", help="Factura de detraccion", domain=[('move_type', '=', 'out_invoice'),
                                                                                                                   ('state', '=', 'posted'),
                                                                                                                   ('detraction_amount', '!=', 0.00)])

    @api.onchange('move_detraction_id')
    def onchange_move_detraction_id(self):
        if self.move_detraction_id:
            self.currency_id = self.move_detraction_id.currency_id
            self.amount = self.move_detraction_id.detraction_amount
            self.is_detraction_pay = True
        else:
            self.amount = 0.00
            self.is_detraction_pay = False
