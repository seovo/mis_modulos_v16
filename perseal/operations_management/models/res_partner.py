# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from pytz import timezone
import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError
import operator
DATE_FORMAT = '%Y-%m-%d'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    simple_interest = fields.Boolean(string='Interés simple')
    document_ids = fields.One2many('operacion.documento', 'deudor_id', string='Documento')
    document_due_ids = fields.Many2many('operacion.documento', string='Documentos',compute='compute_total_due_document')
    total_due_document = fields.Monetary(string='Adeudo Total',compute='compute_total_due_document')
 # COBRANZAS
    # pending_currecy_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id )
    document_pending_ids = fields.Many2many('operacion.documento', string='Documentos pendientes',compute='compute_total_pending_document',readonly=False)
    total_pending_document = fields.Monetary(string='Adeudo Total ', compute='compute_total_pending_document')
    
    # partner_document_pending_ids = fields.Many2many('res.partner')

    @api.depends('document_ids', 'document_ids.state')
    def compute_total_pending_document(self):
        today = datetime.now(timezone('America/Lima')).strftime(DATE_FORMAT)
        rate_today = datetime.strptime(today, DATE_FORMAT).date()
        for line in self:
            line.document_pending_ids = line.document_ids.filtered(lambda x: x.state in ('por_cobrar', 'proceso_pago') and x.due_date <= rate_today)
            total_pending_document = 0.0
            for l in line.document_pending_ids:
                if l.currency_id != self.env.company.currency_id:
                    total_pending_document += l.currency_id._convert(l.net_amount_document, self.env.company.currency_id, self.env.company, today)
                else:
                    total_pending_document += l.net_amount_document
            line.total_pending_document = total_pending_document

    @api.depends('document_ids', 'document_ids.state')
    def compute_total_due_document(self):
        for line in self:
            line.document_due_ids = line.document_ids.filtered(lambda x: x.state not in ('borrador', 'pagado'))
            line.total_due_document = sum([int(l.net_amount_document) for l in line.document_ids.filtered(lambda x: x.state not in ('borrador', 'pagado'))])

    def revisar_tipo_vendedor(self):
        res_partner_category_TVF_id = self.env.ref('operations_management.res_partner_category_TVF')
        res_partner_category_TVC_id = self.env.ref('operations_management.res_partner_category_TVC')
        for partner_id in self:
            if res_partner_category_TVF_id in partner_id.category_id and res_partner_category_TVC_id in partner_id.category_id:
                raise UserError('Las categorías "TipoVendedor:Factor" y "TipoVendedor:Cedente" son excluyentes y no se pueden configurar ambas para un mismo contacto.')

    @api.model_create_multi
    def create(self, vals_list):
        partner_ids = super(ResPartner, self).create(vals_list)
        partner_ids.revisar_tipo_vendedor()
        return partner_ids

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        self.revisar_tipo_vendedor()
        return res

    @api.depends('complete_name', 'email', 'vat', 'state_id', 'country_id', 'commercial_company_name', 'category_id')
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat', 'show_tipo_vendedor')
    def _compute_display_name(self):
        res_partner_category_TVF_id = self.env.ref('operations_management.res_partner_category_TVF')
        res_partner_category_TVC_id = self.env.ref('operations_management.res_partner_category_TVC')
        for partner_id in self:
            if self._context.get('show_tipo_vendedor'):
                if res_partner_category_TVF_id in partner_id.category_id:
                    partner_id.display_name = '{0} (Factor)'.format(partner_id.name)
                elif res_partner_category_TVC_id in partner_id.category_id:
                    partner_id.display_name = '{0} (Cedente)'.format(partner_id.name)
            else:
                super(ResPartner, self)._compute_display_name()

    def open_view_res_partner_follow(self):
        partner_ids = self.search([('document_ids', '!=', False)])
        return {
            'name': 'Seguimiento',
            'res_model': 'res.partner',
            'view_mode': 'form',
            "views": [[self.env.ref('operations_management.partner_follow_up_tree_view').id, "tree"],
                      [self.env.ref('operations_management.partner_follow_up_form_view').id, "form"]],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', partner_ids.ids)],
        }

    def open_view_res_partner_pending(self):
        today = datetime.now(timezone('America/Lima')).strftime(DATE_FORMAT)
        document_pending_ids = self.env['operacion.documento'].search([('state', 'in', ['por_cobrar', 'proceso_pago']), ('due_date','<=', today)])
        document_pending_ids._compute_operacion_ids()
        partner_pending_ids = document_pending_ids.mapped('deudor_id')
        document_ids = self.env['operacion.documento'].search([])
        partner_ids = document_ids.mapped('deudor_id')
        return {
            'name': 'Seguimiento',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'search_view_id': [self.env.ref('operations_management.partner_pending_search_view').id, 'search'],
            "views": [[self.env.ref('operations_management.partner_pending_tree_view').id, "tree"],
                      [self.env.ref('operations_management.partner_pending_form_view').id, "form"]],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', partner_ids.ids)],
            'context': {
                'search_default_pending_ids': True,
                'pending_ids': partner_pending_ids.ids,
            }
        }
        
    def compute_amount_pending(self, document):
        interes = 0
        operadores_list = {"menor_igual": operator.le,
                           "igual": operator.eq,
                           "mayor_igual": operator.ge}
        today = datetime.now(timezone('America/Lima')).date()
        days = (today - document.due_date).days
        liquidacion_line = self.env['operacion.liquidacion.line'].search([('documento_id','=',document.id)], limit=1)
        if liquidacion_line:
            contract = liquidacion_line.liquidacion_id.contrato_id
            for line in contract.line_ids:
                if operadores_list[line.operador_logico](days, line.dias):
                    tasa = line.tasa
                    interes = document.net_amount_document * (tasa/100)
        return interes
            

    def action_register_payment(self):
        sum_amount = 0.0
        for line in self.document_pending_ids.filtered(lambda l: l.register_payment):
            if line.currency_id != line.company_id.currency_id:
                sum_amount += line.currency_id._convert((line.net_amount_document - line.amount_paid), line.company_id.currency_id, line.company_id, datetime.now(pytz.timezone("America/Lima")).strftime('%Y-%m-%d'))
            else:
                sum_amount += (line.net_amount_document - line.amount_paid)
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

