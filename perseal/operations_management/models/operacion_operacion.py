# -*- coding: utf-8 -*-
from pytz import timezone
from datetime import datetime, timedelta
from odoo import fields, models, api
import operator
import pytz
from decimal import Decimal, ROUND_HALF_UP


class OperacionOperacionStage(models.Model):
    _name = 'operacion.operacion.stage'
    _description = 'Operación etapas'

    name = fields.Char('Stage Name')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    fold = fields.Boolean('Folded in Pipeline',default=True,
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    active = fields.Boolean('Activo', default=True)


class OperacionOperacion(models.Model):
    _name = 'operacion.operacion'
    _inherit = 'mail.thread'
    _description = 'Operación'

    name = fields.Char(
        string='Nombre',
        default='/',
    )
    duration_tracking = fields.Json(
        string="Status time",
        help="JSON that maps ids from a many2one field to seconds spent")

    stage_id = fields.Many2one('operacion.operacion.stage',
                               string='Etapa',
                               group_expand="_read_group_stage_id",
                               default=lambda self: self.env.ref('operations_management.operacion_operacion_stage_borrador',
                                                                 raise_if_not_found=False))

    stage_name = fields.Char(related='stage_id.name')

    contrato_id = fields.Many2one(
        comodel_name='operacion.contrato',
        string='Contrato'
    )
    sub_tipo = fields.Selection(selection=[
        ('factoring_con_recurso', 'Factoring con recurso'),
        ('factoring_sin_recurso', 'Factoring sin recurso'),
        ('confirming', 'Confirming'),
    ], string='Sub tipo')
    recurso_ids = fields.Many2many(
        comodel_name='account.tax',
        string='Recursos',
    )
    vendedor_id = fields.Many2one(
        related='contrato_id.vendedor_id',
        string='Vendedor',
    )
    tipo_operacion_id = fields.Many2one(
        comodel_name='operacion.tipo',
        string='Tipo operación',
    )
    fecha = fields.Date(string='Fecha')
    titular_id = fields.Many2one(
        comodel_name='res.partner',
        string='Titular',
    )
    comisionista_id = fields.Many2one(
        comodel_name='res.partner',
        string='Comisionista',
    )
    interes_simple = fields.Boolean(
        string='Interés simple',
    )
    fondo_garantia = fields.Float(
        string='Fondo garantía',
    )
    tem = fields.Float(
        string='TEM',
    )
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('titularizada', 'Titularizada'),
        ('propiedad', 'En propiedad'),
        ('cobranza', 'En cobranza'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),

    ], string='Estado',
        default='borrador',
        group_expand='_read_group_state')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
    )
    total = fields.Float(
        string='Total operación',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        comodel_name='operacion.operacion.line',
        inverse_name='operacion_id',
        string='Líneas',
    )
    liquidation_ids = fields.Many2many('operacion.liquidacion', string='Liquidaciones')
    liquidation_count = fields.Integer(string='NUmero de Liquidaciones', compute='_get_liquidation')
    move_ids = fields.One2many('account.move', 'operacion_id', string='Asientos Contables')
    move_count = fields.Integer(string='Numero de asientos',compute='_compute_move_ids')
    operacion_sold_id = fields.Many2one('operacion.operacion', string='Operacion vendidad')
    operacion_sold = fields.Boolean(string="Operacion vendida")
    additional_term_all = fields.Integer(string='Plazo adicional', compute='_compute_data_pay')
    monetary_interest = fields.Float(string='Tasa Int Moratorio', compute='_compute_data_pay')
    
    def action_state_titularizada(self):
        if not any(move.state in ['draft','cancel'] for move in self.move_ids):
            self.state = 'titularizada'
            for line in self.line_ids:
                line.documento_id.update({'state': 'por_desembolsar'})
                
    def action_state_completada(self):
        if all(line.documento_id.state in ['pagado'] for line in self.line_ids):
            self.state = 'completada'
        
     
    @api.depends('line_ids.date_of_pay')
    def _compute_data_pay(self):
        max_days = 0
        for line in self.line_ids:
            if line.date_of_pay and line.due_date:
                diff_days = (line.date_of_pay - line.due_date).days
                if diff_days > max_days:
                    max_days = diff_days
        self.additional_term_all = max_days if max_days > 0 else 0
        self.monetary_interest = self.contrato_id.get_interest(days=self.additional_term_all)/12 

    @api.model
    def _read_group_state(self,stages, domain, order):
        state = dict(self._fields['state'].selection).keys()
        return state

    @api.depends('move_ids')
    def _compute_move_ids(self):
        self.move_count = len(self.move_ids)

    def action_post(self):
        for line in self.line_ids:
            line.create_journal_entry()
        # self.stage_id = self.env.ref('operations_management.operacion_operacion_stage_titularizada')

    @api.onchange('sub_tipo', 'tem', 'fondo_garantia', 'interes_simple')
    def _onchange_sub_tipo(self):
        for line in self.line_ids:
            line._onchange_documento_id()

    def action_import_operation_document(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {'model': 'operacion.documento'}
        }

    @api.model_create_multi
    def create(self, vals_list):
        operacion_ids = super(OperacionOperacion, self).create(vals_list)
        for operacion_id in operacion_ids:
            prefijo = 'OP{0}{1:02d}-'.format(
                operacion_id.fecha.year,
                operacion_id.fecha.month,
            )
            operaciones_mes_ids = self.search([
                ('name', 'like', prefijo)
            ])
            operacion_id.name = '{0}{1:04d}'.format(prefijo, len(operaciones_mes_ids) + 1)
        return operacion_ids

    @api.onchange('contrato_id')
    def _onchange_contrato_id(self):
        if self.contrato_id:
            self.interes_simple = self.contrato_id.vendedor_id.simple_interest

    def action_vender(self):
        values = {'contrato_id': self.contrato_id.id,
                  'fecha': datetime.now(timezone('America/Lima')).date(),
                  'operacion_sold': True,
                  'tipo_operacion_id': self.env['operacion.tipo'].search([('name', '=', 'Venta')], limit=1).id or False,
                  'line_ids': self.get_info_line(),
        }
        operacion_sold_id = self.create(values)
        self.operacion_sold_id = operacion_sold_id.id
        self.selection_false_lines()

    def get_info_line(self):
        values = []
        for x in self.line_ids:
            if x.seleccionar:
                value = {
                    'cedente_id': x.cedente_id.id,
                    'deudor_id': x.deudor_id.id,
                    'proveedor_id': x.proveedor_id.id,
                    'fch_desembolso': x.fch_desembolso,
                    'fch_vencimiento': x.fch_vencimiento,
                    'currency_id': x.currency_id.id,
                    'company_id': x.company_id.id,
                    'plazo_dias': x.plazo_dias,
                    'monto_fondo_garantia': x.monto_fondo_garantia,
                    'monto_tem': x.monto_tem,
                    'monto_neto': x.monto_neto,
                    'monto': x.monto,
                    'monto_adelanto': x.monto_adelanto,
                    'monto_adelanto_previo': x.monto_adelanto_previo,
                    'liquidacion_factor': x.liquidacion_factor,
                    'pago_factor': x.pago_factor,
                    'documento_id': x.documento_id.id,
                }
                values.append((0, 0, value))
        return values

    def selection_false_lines(self):
        for line in self.line_ids:
            line.seleccionar = False

    def action_liquidate(self):
        self.action_post()
        document_ids = self.line_ids.mapped('documento_id')
        partner_ids = document_ids.mapped('proveedor_id') if self.sub_tipo == 'confirming' else document_ids.mapped('cedente_id')
        liquidation_obj = self.env['operacion.liquidacion']
        for partner in partner_ids:
            if self.sub_tipo == 'confirming':
                line_ids = self.line_ids.filtered(lambda l: l.proveedor_id == partner)
            else:
                line_ids = self.line_ids.filtered(lambda l: l.cedente_id == partner)
            vals = {'beneficiario_id': partner.id,
                    'operacion_id':self.id,
                    'state':'por_cobrar',
                    'contrato_id': self.contrato_id.id,
                    'currency_id': self.currency_id.id,
                    'line_ids': self.create_line_liquidation(line_ids)}
            
            liquidation_id = liquidation_obj.create(vals)
            for l in line_ids:
                l.liquidacion_id = liquidation_id.id
            self.update({'liquidation_ids': [(4, liquidation_id.id, 0)]})
        self.update({'state': 'titularizada'})
                
    
    def action_view_liquidation(self):
        action = {
            'name': 'Liquidaciones',
            'res_model': 'operacion.liquidacion',
            'type': 'ir.actions.act_window',
        }
        if len(self.liquidation_ids) > 1:
            action['view_mode'] = 'tree, form'
            action['domain'] = [('id', 'in', self.liquidation_ids.ids)]
            action['views'] = [(self.env.ref('operations_management.operacion_liquidacion_tree_view').id, 'tree'), (False, 'form')]
        
        else:
            action['view_mode'] = 'form'
            action['res_id'] = self.liquidation_ids[0].id
            action['views'] = [(self.env.ref('operations_management.operacion_liquidacion_form_view').id, 'form')]
        return action

    @api.depends('liquidation_ids')
    def _get_liquidation(self):
        for l in self:
            l.liquidation_count = len(l.liquidation_ids)

    def create_line_liquidation(self, line_ids):
        values = []
        for x in line_ids:
            value = {
                    'cedente_id': x.cedente_id.id,
                    'deudor_id': x.deudor_id.id,
                    'proveedor_id': x.proveedor_id.id,
                    'fch_desembolso': x.fch_desembolso,
                    'fch_vencimiento': x.fch_vencimiento,
                    'currency_id': x.currency_id.id,
                    'company_id': x.company_id.id,
                    'plazo': x.plazo_dias,
                    'contrato_id': self.contrato_id.id,
                    'monto_fdg': x.monto_fondo_garantia,
                    'por_fdg': self.fondo_garantia,
                    'por_tem':self.tem,
                    'monto_tem': x.monto_tem,
                    'net_amount_document': x.monto_neto,
                    'monto': x.monto,
                    'monto_adelanto': x.monto_adelanto,
                    'monto_adelanto_previo': x.monto_adelanto_previo,
                    'liquidacion_factor': x.liquidacion_factor,
                    'pago_factor': x.pago_factor,
                    'documento_id': x.documento_id.id,
            }
            values.append((0, 0, value))
        return values

    def action_open_import_file(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cargar archivo',
            'res_model': 'file.upload.operation',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('operations_management.file_upload_operation_form_view').id,
        }

    def button_open_journal_entry(self):

        return {
            'name': "Asiento contable",
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.move_ids.ids)],
        }
        
    def action_view_operacion_sold(self):
        return {
            'name': "Operacion vendida",
            'type': 'ir.actions.act_window',
            'res_id': self.operacion_sold_id.id,
            'res_model': 'operacion.operacion',
            'view_mode': 'form',
        }



class OperacionOperacionLine(models.Model):
    _name = 'operacion.operacion.line'
    _description = 'Operación detalle'

    operacion_id = fields.Many2one(
        comodel_name='operacion.operacion',
        string='Operación',
    )
    plazo_dias = fields.Integer(string='Plazo en dias')
    fondo_garantia = fields.Float(
        related='operacion_id.fondo_garantia',
        string='Fondo garantía',
        store=True,
    )
    monto_fondo_garantia = fields.Float(
        string='Monto fondo garantía',
    )
    tem = fields.Float(
        related='operacion_id.tem',
        string='TEM',
        store=True,
    )
    monto_tem = fields.Float(
        string='Monto TEM',
    )
    pago_factor = fields.Float(
        string='Pago factor',
    )
    monto_neto = fields.Monetary(
        related='documento_id.net_amount_document',
        string='Monto neto documento',
        store=True,
    )
    monto_adelanto = fields.Float(
        string='Monto adelanto',
    )
    monto_adelanto_previo = fields.Float(
        string='Monto adelanto previo',
    )
    liquidacion_factor = fields.Float(
        string='Liquidación factor',
    )
    documento_id = fields.Many2one(
        comodel_name='operacion.documento',
        string='Documento',
    )
    liquidacion_id = fields.Many2one(
        comodel_name='operacion.liquidacion',
        string='Liquidación',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    fch_desembolso = fields.Date(string='Fecha desembolso')
    fch_vencimiento = fields.Date(string='Fecha vencimiento')
    cedente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cedente',
        related='documento_id.cedente_id',
        readonly=False,
    )
    deudor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Deudor',
        related='documento_id.deudor_id',
        readonly=False,
    )
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
        related='documento_id.proveedor_id',
        readonly=False,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
    )
    seleccionar = fields.Boolean(
        string='Seleccionar'
    )
    seleccionar_backup = fields.Boolean(
        string='Seleccionar backup'
    )
    monto = fields.Float(
        string='Monto'
    )
    pago_factor = fields.Float(
        string='Pago a factor'
    )
    
    due_date = fields.Date(string='Fecha de vencimiento', related='documento_id.due_date')
    date_of_pay = fields.Date(string='Fecha de pago')
    additional_term_all = fields.Integer(string='Plazo adicional', related='operacion_id.additional_term_all')
    monetary_interest = fields.Float(string='Tasa Int Moratorio', related='operacion_id.monetary_interest')
    additional_interest = fields.Float(string='Intereses Adicionales', compute='_compute_additional_interest')
    default_interest = fields.Float(string='Intereses Moratorio', compute='_compute_additional_interest')
    return_guarantee = fields.Monetary(string='F. Garantia por devolver',compute='_compute_additional_interest')
    
    
    @api.depends('date_of_pay')
    def _compute_additional_interest(self):
        for line in self:
            tem = line.tem/100
            interest = line.monetary_interest/100
            line.additional_interest = round((line.monto_neto - line.monto_fondo_garantia) * (pow(1 + tem, line.additional_term_all / 30) - 1), 2)
            line.default_interest = round((line.monto_neto - line.monto_fondo_garantia) * (pow(1 + interest, line.additional_term_all / 30) - 1), 2)
            line.return_guarantee = line.monto_fondo_garantia - line.additional_interest - line.default_interest
    
                
    @api.onchange('documento_id')
    def _onchange_documento_id(self):
        fch_desembolso = False
        fch_vencimiento = False
        currency_id = False
        if self.documento_id:
            fch_desembolso = self.documento_id.disbursement_date
            fch_vencimiento = self.documento_id.due_date
            currency_id = self.documento_id.currency_id
        self.fch_desembolso = fch_desembolso
        self.fch_vencimiento = fch_vencimiento
        self.currency_id = currency_id
        self.calcular_montos()

    def calcular_montos(self):
        self.monto_fondo_garantia = self.monto_neto * self.fondo_garantia / 100
        self.monto_tem = self.monto_neto * self.tem / 100
        self.plazo_dias = (self.fch_vencimiento - self.fch_desembolso).days if self.fch_vencimiento and self.fch_desembolso else 0
        diferencia = self.monto_neto - self.monto_fondo_garantia
        if not self.operacion_id.interes_simple:
            if self.operacion_id.sub_tipo == 'factoring_sin_recurso':
                valor = diferencia - (diferencia * ((1 + (self.tem / 100)) ** (self.plazo_dias / 30) - 1))
            else:
                valor = diferencia - (diferencia * ((1 + (self.tem / 100)) ** (self.plazo_dias / 30) - 1) * 1.18)
        else:
            if self.operacion_id.sub_tipo == 'factoring_sin_recurso':
                valor = diferencia - (diferencia * ((self.tem / 100) * (self.plazo_dias / 30)))
            else:
                valor = diferencia - (diferencia * ((self.tem / 100) * (self.plazo_dias / 30)) * 1.18)
        self.monto = valor
        self.pago_factor = self.monto - self.liquidacion_factor

    @api.onchange('liquidacion_factor')
    def _onchange_liquidacion_factor(self):
        self.pago_factor = self.monto - self.liquidacion_factor

    def create_journal_entry(self):
        journal = self.env['account.journal'].search([('name', '=', 'Operaciones')], limit=1)
        date_today = fields.datetime.now(pytz.timezone("America/Lima"))
        data = {'ref': 'Operacion/' + self.documento_id.name,
                'date': date_today,
                'move_type': 'entry',
                'journal_id': journal.id,
                'line_ids': self._prepare_move_line(date_today),
                }
        move_id = self.env['account.move'].create(data)
        # move_id._onchange_date()
        move_id.action_post()
        self.operacion_id.update({'move_ids': [(4, move_id.id,0)]})
        # self.operacion_id.update({'state': 'por_desembolsar'})

    def _prepare_move_line(self, date_today):
        currency = self.currency_id if self.currency_id else self.env.company.currency_id
        tipo_operacion_id = self.operacion_id.tipo_operacion_id
        company_id = self.operacion_id.company_id
        interes_currency = self.monto_neto - self.monto_fondo_garantia - self.monto
        if self.currency_id == company_id.currency_id:
            monto_neto = self.monto_neto
            monto_fondo_garantia = self.monto_fondo_garantia
            monto = self.monto
        else:
            monto_neto = self.currency_id._convert(self.monto_neto, company_id.currency_id, company_id , date_today)
            monto_fondo_garantia = self.currency_id._convert(self.monto_fondo_garantia, company_id.currency_id, company_id , date_today)
            monto = self.currency_id._convert(self.monto, company_id.currency_id, company_id , date_today)
            interes = monto_neto - monto_fondo_garantia - monto
        data_line_cedente = {'account_id': tipo_operacion_id.get_account('ingreso'),
                            'partner_id': self.cedente_id.id,
                            'name': self.documento_id.num_documento,
                            'currency_id': currency.id,
                            'amount_currency': self.monto_neto,
                            'credit': 0.0,
                            'debit': monto_neto}
        data_line_deudor = {'account_id': tipo_operacion_id.get_account('fdg'),
                             'partner_id': self.deudor_id.id,
                             'name': self.documento_id.num_documento,
                             'currency_id': currency.id,
                             'amount_currency': self.monto_fondo_garantia * -1,
                             'credit': monto_fondo_garantia,
                             'debit': 0.0}
        data_line_titular = {'account_id': tipo_operacion_id.get_account('interes'),
                            'partner_id': self.proveedor_id.id,
                            'name': self.documento_id.num_documento,
                            'currency_id': currency.id,
                            'amount_currency': interes_currency * -1,
                            'credit': interes,
                            'debit': 0.0}
        data_line_two = {'account_id': tipo_operacion_id.get_account('desembolso'),
                         'partner_id': self.operacion_id.vendedor_id.id,
                         'name': self.documento_id.num_documento,
                         'currency_id': currency.id,
                         'amount_currency': self.monto * -1,
                         'credit': monto,
                         'debit': 0.0}
        return [(0, 0, data_line_cedente),(0, 0, data_line_deudor),(0, 0, data_line_titular), (0, 0, data_line_two)]



