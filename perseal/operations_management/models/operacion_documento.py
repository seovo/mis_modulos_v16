# -*- coding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import operator


class OperacionDocumento(models.Model):
    _name = 'operacion.documento'
    _inherit = 'mail.thread'
    _description = 'Documento'

    name = fields.Char(string='Número de documento')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
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
    issue_date = fields.Date(string='Fecha de emisión')
    due_date = fields.Date(string='Fecha de vencimiento')
    disbursement_date = fields.Date(string='Fecha de desembolso')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
    )
    net_amount_document = fields.Monetary(string='Monto neto')
    tipo_documento_id = fields.Many2one(
        comodel_name='l10n_latam.document.type',
        string='Tipo de documento',
    )
    num_documento = fields.Char(string='Núm. documento')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('por_desembolsar', 'Por desembolsar'),
        ('por_cobrar', 'Por cobrar'),
        ('proceso_pago', 'Proceso de pago'),
        ('pagado', 'Pagado'),
    ], string='Estado', default='borrador')
    company_partner_category_proveedor_id = fields.Many2one(
        string='Categoría proveedor',
        related='company_id.company_partner_category_proveedor_id'
    )
    company_partner_category_cedente_id = fields.Many2one(
        string='Categoría cedente',
        related='company_id.company_partner_category_cedente_id'
    )
    company_partner_category_deudor_id = fields.Many2one(
        string='Categoría deudor',
        related='company_id.company_partner_category_deudor_id'
    )
    operacion_ids = fields.Many2many(
        comodel_name='operacion.operacion',
        string='Operaciones',
        compute='_compute_operacion_ids'
    )
    
    operacion_id = fields.Many2one(
        comodel_name = 'operacion.operacion',
        string = 'Operaciones',
        store = True,
        
    )
    operacion_line_id = fields.Many2one(
        comodel_name = 'operacion.operacion.line',
        string='Linea de operacion',
        compute = '_compute_operacion_ids')

    monto_fondo_garantia = fields.Float(
        related='operacion_line_id.monto_fondo_garantia',
        string='Monto fondo garantía',
    )
    
    debt_amount = fields.Float(string='Monto adeudado', compute = '_compute_operacion_ids')
    operacion_numero = fields.Char(string='Numero de operacion')
    register_payment = fields.Boolean(string='Select.')
    payment_ids = fields.Many2many('account.payment', string='pagos', copy=False)
    payment_count = fields.Integer(string='Número de pagos', copy=False, compute='_compute_payment_count')
    operacion_line_ids = fields.One2many('operacion.operacion.line', 'documento_id', string='Linea de operacion')
    amount_paid = fields.Float(string="Monto pagado", compute='_compute_payment_count')
    
    
    @api.depends('payment_ids.state', 'payment_ids.is_matched', 'payment_ids')
    def _compute_payment_count(self):
        for line in self:
            line.payment_count = len(line.payment_ids)
            amount_total = 0
            payment_ids = line.payment_ids.filtered(lambda l: l.state == 'posted')
            for pay in payment_ids:
                if line.currency_id == pay.currency_id:
                    amount_total += pay.amount
                else:
                    amount_total += pay.currency_id._convert(pay.amount, line.currency_id, line.company_id, pay.date or datetime.today(pytz.timezone("America/Lima")).strftime('%Y-%m-%d'))
            line.amount_paid = amount_total
            if line.amount_paid > 0.0:
                line.state = 'proceso_pago'
            if line.amount_paid >= round(line.net_amount_document,2):
                if not any(l.is_matched==False for l in payment_ids):
                    line.state = 'pagado'
                    line.operacion_line_id.operacion_id.action_state_completada()
        

    @api.model_create_multi
    def create(self, vals):
        res = super(OperacionDocumento, self).create(vals)
        operacion_line_obj = self.env['operacion.operacion.line']
        for line in res:
            if line.operacion_numero:
                operacion_id = self.env['operacion.operacion'].search([('name', '=', line.operacion_numero)],limit=1)
                if operacion_id:
                    vals_operacion_line = {'operacion_id': operacion_id.id,
                                           'documento_id': line.id}
                    operacion_line_id = operacion_line_obj.create(vals_operacion_line)
                    operacion_line_id._onchange_documento_id()
        res._onchange_name()
        return res
    
    def write(self, vals):
        res = super(OperacionDocumento, self).write(vals)
        return res

    def _compute_operacion_ids(self):
        for line in self:
            line.debt_amount = 0.0
            operacion_line_ids = self.env['operacion.operacion.line'].search([('documento_id', '=', line.id)])
            if operacion_line_ids:
                line.operacion_ids = operacion_line_ids.mapped('operacion_id')
                operacion_line_id = operacion_line_ids.filtered(lambda l: not l.operacion_id.operacion_sold_id and l.operacion_id.operacion_sold == False) or False
                
                if operacion_line_id:
                    line.operacion_line_id = operacion_line_id[0].id
                    line.debt_amount = line.get_debt_amount(line.operacion_line_id)
                else:
                    line.operacion_line_id = False
                    
            else:
                line.operacion_ids = False
                line.operacion_line_id = False
                
    def get_debt_amount(self, operacion_line_id):
        interes = 0
        operadores_list = {"menor_igual": operator.le,
                           "igual": operator.eq,
                           "mayor_igual": operator.ge}
        today = datetime.now(timezone('America/Lima')).date()
        days = (today - self.due_date).days
        contract = operacion_line_id.operacion_id.contrato_id
        for line in contract.line_ids:
            if operadores_list[line.operador_logico](days, line.dias):
                tasa = line.tasa
                interes = self.net_amount_document * (tasa/100)
        return interes

    def action_register_payment(self):
        sum_amount = 0.0
        if self.currency_id != self.company_id.currency_id:
            sum_amount += self.currency_id._convert((self.net_amount_document - self.amount_paid), self.company_id.currency_id, self.company_id, datetime.now(pytz.timezone("America/Lima")).strftime('%Y-%m-%d'))
        else:
            sum_amount += (self.net_amount_document - self.amount_paid)
        return {
            'name': 'Registrar pago',
            'res_model': 'liquidacion.payment.register',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_partner_id': self.id,
                        'default_amount': sum_amount,
                        'default_source_amount': sum_amount},
        }

    def action_por_desembolsar(self):
        self.state = 'por_desembolsar'

    def action_por_cobrar(self):
        self.state = 'por_cobrar'

    def action_proceso_pago(self):
        self.state = 'proceso_pago'

    def action_pagado(self):
        self.state = 'pagado'

    @api.onchange('proveedor_id', 'num_documento')
    def _onchange_name(self):
        for record in self:
            if record.proveedor_id:
                record.name = '{0}-{1}'.format(
                    record.proveedor_id.vat,
                    record.num_documento if record.num_documento else '',
                )
            else:
                record.name = ''

    def action_view_payment(self):
        return {
            'name': 'Pagos',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'account.payment',
            'res_id': self.payment_ids.id,
            'target': 'current',
        }
        
    def action_automatic_entry(self):
        return {
            'name': 'Documento',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': 'operacion.documento',
            'res_id': self.id,
        }
