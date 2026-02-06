# -*- coding: utf-8 -*-
from locale import currency

from odoo import fields, models, api
from datetime import datetime

PAYMENT_STATE_SELECTION = [
        ('not_paid', 'No pagadas'),
        ('in_payment', 'En proceso de pago'),
        ('paid', 'Pagado'),
        ('partial', 'Pagado Parcialmente'),
]


class OperacionLiquidacion(models.Model):
    _name = 'operacion.liquidacion'
    _inherit = 'mail.thread'
    _description = 'Liquidación'

    name = fields.Char(string='Nombre')
    beneficiario_id = fields.Many2one(
        comodel_name='res.partner',
        string='Beneficiario',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    operacion_id = fields.Many2one(
        comodel_name='operacion.operacion',
        string='Operaciones'
    )
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Cuenta bancaria',
    )
    contrato_id = fields.Many2one(
        comodel_name='operacion.contrato',
        string='Contrato',
    )
    disbursement_date = fields.Date(string='Fecha de desembolso')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('por_cobrar', 'Por cobrar'),
        ('proceso_pago', 'Proceso de pago'),
        ('pagado', 'Pagado'),
    ], string='Estado', default='borrador')
    company_partner_category_beneficiario_id = fields.Many2one(
        string='Categoría proveedor',
        related='company_id.company_partner_category_beneficiario_id'
    )
    line_ids = fields.One2many(
        comodel_name='operacion.liquidacion.line',
        inverse_name='liquidacion_id',
        string='Líneas de detalle',
    )
    currency_id = fields.Many2one('res.currency', string='Moneda',default=lambda self: self.env.company.currency_id)

    valor = fields.Float(string='Valor', compute='_get_value_lines', store=True)

    payment_state = fields.Selection(
        selection=PAYMENT_STATE_SELECTION,
        string="Payment Status",
        store=True, readonly=True,
        copy=False,
        tracking=True,
    )

    payment_ids = fields.One2many('account.payment','liquidacion_id', string='pagos',copy=False)
    payment_count = fields.Integer(string='Numero de pagos',compute='compute_amount_payment')
    amount_payment = fields.Float(string='Monto pagado', compute='compute_amount_payment', store=True)
    move_id = fields.Many2one('account.move', string='Asiento contable')

    def action_post(self):
        journal = self.env['account.journal'].browse(56)
        data = {'ref': 'Liquidacion' + self.name,
                'date': fields.datetime.now(),
                'move_type': 'entry',
                'journal_id': journal.id,
                'line_ids':self._prepare_move_line(journal),
                }
        move_id = self.env['account.move'].create(data)
        self.move_id = move_id
        self.update({'state':'por_cobrar'})

    def _prepare_move_line(self,journal):
        currency = self.currency_id if self.currency_id else self.env.company.currency_id
        data_line_one = {'account_id': self.beneficiario_id.property_account_payable_id.id,
                         'partner_id': self.beneficiario_id.id,
                         'name': 'Liquidacion',
                         'currency_id': currency.id,
                         'amount_currency': self.valor * -1,
                         'credit': self.valor,
                         'debit': 0.0}
        data_line_two = {'account_id': journal.default_account_id.id,
                         'partner_id': self.beneficiario_id.id,
                         'name': 'Liquidacion',
                         'currency_id': currency.id,
                         'amount_currency': self.valor,
                         'credit': 0.0,
                         'debit': self.valor}
        return [(0, 0, data_line_one), (0, 0, data_line_two)]

    @api.depends('payment_ids.state', 'payment_ids.is_matched', 'payment_ids')
    def compute_amount_payment(self):
        for pay in self:
            payment_ids = pay.payment_ids.filtered(lambda l: l.state == 'posted')
            amount_total = 0
            for line in payment_ids:
                if line.currency_id == pay.currency_id:
                    amount_total += line.amount
                else:
                    amount_total += line.currency_id._convert(line.amount, pay.currency_id, line.company_id, line.date or datetime.today().strftime('%Y-%m-%d'))
            pay.amount_payment = amount_total
            if pay.amount_payment >= round(pay.valor,2):
                pay.state = 'proceso_pago'
                pay.operacion_id.state = 'propiedad'
                if not any(l.is_matched==False for l in payment_ids):
                    pay.state = 'pagado'
                    pay.operacion_id.state = 'cobranza'
                    pay.line_ids.update_state_document()
            pay.payment_count = len(pay.payment_ids) 


    @api.depends('line_ids', 'line_ids.net_amount_document')
    def _get_value_lines(self):
        for line in self:
            line.valor = round(sum(l.monto for l in line.line_ids), 2)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('operacion.liquidacion')
        return super().create(vals_list)

    def action_register_payment(self):
        return {
            'name': 'Registrar pago',
            'res_model': 'liquidacion.payment.register',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_amount':self.valor - self.amount_payment,
                        'default_currency_id': self.company_id.currency_id.id,
                        'partner_id':self.beneficiario_id.id},
        }

    def button_open_journal_entry(self):

        self.ensure_one()
        return {
            'name': "Asiento contable",
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }
        
    def action_open_view_operacion(self):

        return {
            'name': "Operacion",
            'type': 'ir.actions.act_window',
            'res_model': 'operacion.operacion',
            'context': {'create': False},
            'view_mode': 'form',
            'views': [(self.env.ref('operations_management.operacion_operacion_form_view').id, 'form')],
            'res_id': self.operacion_id.id,
        }
        
    def button_open_account_payment(self):
        self.ensure_one()
        return {
            'name': "Pagos",
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
            'views': [(self.env.ref('account.view_account_payment_tree').id, 'list'),
                      (self.env.ref('account.view_account_payment_form').id, 'form')],
            'view_mode': 'list, form',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }
        
    def action_print_liquidacion(self):
        data = {}
        return self.env.ref('operations_management.action_report_operacion_liquidacion_pdf').report_action(self, data=data)



class OperacionLiquidacionLine(models.Model):
    _name = 'operacion.liquidacion.line'
    _description = 'Línea de liquidación'

    liquidacion_id = fields.Many2one(
        comodel_name='operacion.liquidacion',
        string='Liquidación',
    )
    contrato_id = fields.Many2one(
        comodel_name='operacion.contrato',
        string='Contrato',
    )
    cedente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cedente',
    )
    deudor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Deudor',
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    fch_desembolso = fields.Date(string='Fecha desembolso')
    fch_vencimiento = fields.Date(string='Fecha vencimiento')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
    )
    net_amount_document = fields.Monetary(string='Monto neto')
    plazo = fields.Integer(string='Plazo en dias')
    monto = fields.Float(string='Monto')
    por_fdg = fields.Float(string='% FDG')
    monto_fdg = fields.Float(string='Monto FDG')
    por_tem = fields.Float(string='% TEM')
    monto_tem = fields.Float(string='Monto TEM')
    monto_adelanto = fields.Float(string='Monto adelanto')
    monto_adelanto_previo = fields.Float(string='Monto adelanto previo')
    liquidacion_factor = fields.Float(string='Liquidación factor')
    pago_factor = fields.Float(string='Pago a factor')
    documento_id = fields.Many2one(comodel_name='operacion.documento', string='Documento',)
    
    
    def update_state_document(self):
        for line in self:
            line.documento_id.update({'state': 'por_cobrar'})


