# -*- coding: utf-8 -*-

import re

from odoo import fields, models, api
import operator

PATRON = r'\d+$'


class OperacionContrato(models.Model):
    _name = 'operacion.contrato'
    _inherit = 'mail.thread'
    _description = 'Contrato'

    name = fields.Char(string='Nombre')
    vendedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendedor',
    )
    recurso_ids = fields.Many2many(
        comodel_name='account.tax',
        string='Recursos',
    )
    start_date = fields.Date(string='Fecha inicio')
    end_date = fields.Date(string='Fecha fin')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        comodel_name='operacion.contrato.line',
        inverse_name='contrato_id',
        string='Detalles',
    )
    check_contrato = fields.Boolean(string='Contrato')
    check_ficha_ruc = fields.Boolean(string='Ficha RUC')
    check_dni_rep = fields.Boolean(string='DNI representantes')
    check_vig_pod = fields.Boolean(string='Vigencia de poder')
    check_fich_cli = fields.Boolean(string='Ficha de cliente')
    check_copia_lit = fields.Boolean(string='Copia literal (opcional)')
    check_doc_adi = fields.Boolean(string='Documentos adicionales (opcional)')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador')
    res_partner_category_TVF_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoría TipoVendedor:Factor',
        default=lambda self: self.env.ref('operations_management.res_partner_category_TVF'),
    )
    res_partner_category_TVC = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoría TipoVendedor:Cedente',
        default=lambda self: self.env.ref('operations_management.res_partner_category_TVC'),
    )

    @api.onchange('vendedor_id', 'start_date')
    def _onchange_name(self):
        for record in self:
            if record.vendedor_id and record.start_date:
                if record.name:
                    name_fraccionado = record.name.split('-')
                    name_fraccionado[1] = record.vendedor_id.vat if record.vendedor_id.vat else ''
                    record.name = '-'.join(name_fraccionado)
                else:
                    name = 'P-{0}-{1}-'.format(
                        record.vendedor_id.vat if record.vendedor_id.vat else '',
                        record.start_date.year if record.start_date else '',
                    )
                    contrato_ids = record.search([
                        # ('name', 'ilike', name),
                        ('id', '!=', record._origin.id if isinstance(record.id, models.NewId) else record.id),
                        ('company_id', '=', record.env.company.id)
                    ])
                    if contrato_ids:
                        nombres = contrato_ids.mapped('name')
                        numeros = []
                        for cadena in nombres:
                            numeros_encontrados = re.findall(PATRON, cadena)
                            numeros.extend(map(int, numeros_encontrados))
                        maximo_numero = max(numeros)
                        record.name = '{0}{1:04d}'.format(name, maximo_numero + 1)
                    else:
                        record.name = '{0}0001'.format(name)
            else:
                record.name = ''

    def aprobar(self):
        self.state = 'aprobado'

    def cancelar(self):
        self.state = 'cancelado'
        
    def get_interest(self, days):
        operadores_list = {"menor_igual": operator.le,
                           "igual": operator.eq,
                           "mayor_igual": operator.ge}
        for line in self.line_ids:
            if operadores_list[line.operador_logico](days, line.dias):
                interest = line.tasa
        return interest


class OperacionContratoLine(models.Model):
    _name = 'operacion.contrato.line'
    _description = 'Línea de contrato'

    contrato_id = fields.Many2one(
        comodel_name='operacion.contrato',
        string='Contrato',
    )
    name = fields.Char(string='Descripción')
    operador_logico = fields.Selection(selection=[
        ('menor_igual', '<='),
        ('igual', '='),
        ('mayor_igual', '>='),
    ],
        string='Operador lógico',
    )
    dias = fields.Integer(string='Días')
    tasa = fields.Float(string='Tasa (%)')
