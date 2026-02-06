# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError

STATE = [('1', 'Se informa en el periodo'),
         ('2', 'Se informo en el periodo anterior'),
         ('3', 'Para corregir un informe anterior')]


class ReportPle054(models.Model):
    _name = 'report.ple.05.4'
    _inherit = ['report.ple']
    _description = 'Registro Diario'

    line_ids = fields.One2many(comodel_name='report.ple.05.4.line', inverse_name='ple_id', string='Detalle del libro', readonly=True)
    state_opportunity = fields.Selection(STATE,
                                         default='1',
                                         required=True,
                                         string="Estado de la operacion")

    @api.model
    def create(self, vals):
        res = super(ReportPle054, self).create(vals)
        res.update({'name': self.env['ir.sequence'].next_by_code(self._name)})
        return res

    def action_generate(self):
        prefix = "LE"
        company_vat = self.env.user.company_id.partner_id.vat or ''
        date_start = self.date_from
        date_end = self.date_to
        year, month = str(fields.Date().from_string(date_start).year), str(
            fields.Date().from_string(date_start).month).rjust(2, "0")
        currency = 2 if self.currency_id.name in ['USD'] else 1  # USD=2 /PEN=1
        template = "{}{}{}{}00{}00{}{}{}{}.txt"

        domain = []
        moves_obj = self.env['account.account'].search(domain, order='code asc')
        self.create_lines(moves_obj)
        if self.type_report in ['normal']:
            # purchase report normal 050200
            data = self._get_content(self.line_ids, year, month)
            filename = template.format(
                prefix, company_vat, year, month, '050400', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}

        self.action_generate_ple(value)

    def create_lines(self, moves_obj):
        self.line_ids.unlink()
        for x, line in enumerate(moves_obj, 1):
            self.env['report.ple.05.4.line'].create({
                'account_id': line.id,
                'ple_id': self.id,
                'state_opportunity': self.state_opportunity,
                # 'move_name': u'{}{}'.format(line.move_id.l10n_pe_operation_type_sunat, x)
            })

    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        template = '{period}|{codigo_cuenta_desagregado}|{descripcion_cuenta_desagregado}|' \
                   '{codigo_cuenta_tributario}|{descripcion_cuenta_tributario}|' \
                   '{codigo_cuenta_corporativa}|{descripcion_cuenta_corporativa}|{state_opportunity}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=str(v_anio) + str(v_mes) + "01",
                codigo_cuenta_desagregado=(line.codigo_cuenta_desagregado or '')[:24],
                descripcion_cuenta_desagregado=line.descripcion_cuenta_desagregado,
                codigo_cuenta_tributario=line.codigo_cuenta_tributario,
                descripcion_cuenta_tributario=line.descripcion_cuenta_tributario,
                codigo_cuenta_corporativa=line.codigo_cuenta_corporativa,
                descripcion_cuenta_corporativa=line.descripcion_cuenta_corporativa,
                state_opportunity=line.state_opportunity or '',
            )
        return data


class ReportPle054Line(models.Model):
    _name = 'report.ple.05.4.line'
    # _order = 'fecha_contable'
    _description = 'Detalle de registro diario'

    def _get_document_types(self):
        records = self.env["catalog.element"].search_read(
            [('table_id.code', 'ilike', 'PE.SUNAT.PLE_TABLE17')],
            fields=['name', 'description'])
        return [(r['name'], r['description']) for r in records]

    period = fields.Char(string='Periodo', compute='_compute_data')
    account_id = fields.Many2one('account.account', string='Cuenta')
    codigo_cuenta_desagregado = fields.Char(string="Código cuenta contable desagregado", compute='_compute_data',)
    descripcion_cuenta_desagregado = fields.Char(string="Descripcion cuenta contable desagregado", compute='_compute_data',)
    codigo_cuenta_tributario = fields.Selection('_get_document_types', string="Código cuenta contable tributario", default='01',)
    descripcion_cuenta_tributario = fields.Char(string="Descripcion cuenta contable tributario", compute='_compute_data',)
    codigo_cuenta_corporativa = fields.Char(string="Código cuenta contable corporativa", compute='_compute_data')
    descripcion_cuenta_corporativa = fields.Char(string="Descripcion cuenta contable corporativa", compute='_compute_data',)
    state_opportunity = fields.Selection(STATE, string='Estado')
    ple_id = fields.Many2one(comodel_name='report.ple.05.4')

    @api.depends('account_id')
    def _compute_data(self):

        def get_state(date, date_from, date_to):
            v_state = '1'  # Por defecto
            if date >= date_from and date <= date_to:
                v_state = '1'
            else:
                v_state = '8'
            return v_state

        def get_description(account):
            records = self.env["catalog.element"].search([('table_id.code', 'ilike', 'PE.SUNAT.PLE_TABLE17'), ('name', '=', account)], limit=1)
            if records:
                records = records.description
            else:
                records = ''
            return records

        def get_year_month(date):
            return '{}{}'.format(str(fields.Date().from_string(date).year),
                                 str(fields.Date().from_string(date).month).rjust(2, "0"))

        self.mapped(lambda x: x.update({
            'period': '{}01'.format(get_year_month(x.ple_id.date_from)),
            'codigo_cuenta_desagregado': x.account_id.code,
            'descripcion_cuenta_desagregado': x.account_id.name[:100],
            # 'codigo_cuenta_tributario': '01',
            'descripcion_cuenta_tributario': get_description(x.codigo_cuenta_tributario),
            'codigo_cuenta_corporativa': '',
            'descripcion_cuenta_corporativa': '',
            # 'state_opportunity': get_state(x.ple_id.date_from, x.ple_id.date_from, x.ple_id.date_to),
        }))

