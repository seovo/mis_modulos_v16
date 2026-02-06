# -*- coding: utf-8 -*-

import io
import base64
import pytz
import math

from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


class Teletransfer(models.TransientModel):
    _name = 'teletransfer'
    _description = 'Teletransfer'

    def _get_banco_id(self):
        return self.env['res.bank'].search([('name', '=', 'Banco de Crédito del Perú')], limit=1)

    def _get_cuenta_id(self):
        banco_id = self.env['res.bank'].search([('name', '=', 'Banco de Crédito del Perú')], limit=1)
        return self.env['res.partner.bank'].search([('bank_id', '=', banco_id.id)], limit=1)

    banco_id = fields.Many2one(
        comodel_name='res.bank',
        string='Banco',
        default=_get_banco_id,
    )
    cuenta_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Cuentas bancarias',
        default=_get_cuenta_id,
    )
    tipo = fields.Selection(selection=[
        ('A', 'Archivo de actualización'),
        ('R', 'Archivo de reemplazo'),
    ], string='Tipo', default='A')
    cliente = fields.Selection(selection=[
        ('T', 'Todos los clientes'),
        ('E', 'Clientes específicos'),
    ], string='Clientes', default='T')
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Clientes específicos',
    )
    tipo_doc = fields.Selection(selection=[
        ('T', 'Todos los tipos de documento'),
        ('E', 'Tipos de documento específicos'),
    ], string='Tipos de documentos', default='T')
    document_type_ids = fields.Many2many(
        comodel_name='l10n_latam.document.type',
        string='Documentos específicos',
    )
    fecha = fields.Selection(selection=[
        ('T', 'Todos las fechas'),
        ('E', 'Fechas específicas'),
    ], string='Fecha de comprobante', default='T')
    fecha_inicial = fields.Date(string='Fecha inicial')
    fecha_final = fields.Date(string='Fecha final')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
    )
    sin_teletransfer = fields.Boolean(
        string='Comprobantes sin usar en teletransfer',
        default=True,
    )
    line_ids = fields.One2many(
        comodel_name='teletransfer.line',
        inverse_name='teletransfer_id',
        string='Detalles',
    )
    filecontent = fields.Binary(string='Archivo')

    def generar_teletransfer(self):
        if self.line_ids:
            currency_ids = self.line_ids.mapped('currency_id')
            if len(currency_ids) > 1:
                raise UserError('No es posible crear un teletransfer con múltiples divisas en las líneas de detalle.')

            numero_cuenta = self.cuenta_id.acc_number.split('-')
            company_name = self.env.company.name
            mnt_total = int(self.my_round(sum(self.line_ids.mapped('amount_total_signed')), 2) * 100)

            txt_cabecera = 'CC{0}{1}{2}C{3:40}{4}{5:09d}{6:015d}{7}000000{8:157}'.format(
                numero_cuenta[0],  # 0
                numero_cuenta[2],  # 1
                numero_cuenta[1],  # 2
                self.caracteres_especiales(company_name.split(' - ')[0] if ' - ' in company_name else company_name[:40]),  # 3
                datetime.now(pytz.timezone('America/Lima')).strftime('%Y%m%d'),  # 4
                len(self.line_ids),  # 5
                mnt_total,  # 6
                self.tipo,  # 7
                '',  # 8
            )

            txt_detalle = ''
            for line_id in self.line_ids:
                if numero_cuenta[2] == "0":
                    if line_id.currency_id.name != 'PEN':
                        raise UserError('La moneda de la cuenta seleccionada y la de los comprobantes no es la misma.')
                elif numero_cuenta[1] == "1":
                    if line_id.currency_id.name != 'USD':
                        raise UserError('La moneda de la cuenta seleccionada y la de los comprobantes no es la misma.')
                txt_detalle += 'DD{0}{1}{2}{3:014d}{4:40}{5:30}{6}{7}{8:015d}{9:015d}{10:09d}{11}{12:>20}{13:016d}{14:61}\n'.format(
                    numero_cuenta[0],  # 0
                    numero_cuenta[2],  # 1
                    numero_cuenta[1],  # 2
                    int(line_id.move_id.partner_id.vat),  # 3
                    self.caracteres_especiales(line_id.move_id.partner_id.name),  # 4
                    line_id.move_id.partner_id.vat,  # 5
                    fields.Date.to_string(line_id.move_id.invoice_date).replace('-', ''),  # 6
                    fields.Date.to_string(line_id.move_id.invoice_date_due).replace('-', ''),  # 7
                    int(self.my_round(line_id.amount_total_signed, 2) * 100),  # 8
                    0,  # 9
                    int(self.my_round(line_id.amount_total_signed, 2) * 100),  # 10
                    ' ' if self.tipo == 'R' else line_id.tipo,  # 11
                    line_id.move_id.name.replace('-', ''),  # 12
                    int(line_id.move_id.partner_id.vat),  # 13
                    '',  # 14
                )
                line_id.move_id.teletransfer = True

            txt_total = '{0}\n{1}'.format(txt_cabecera, txt_detalle)
            output = io.BytesIO(io.StringIO(txt_total).read().encode('utf8'))
            self.filecontent = base64.b64encode(output.read())
            file_name = 'teletransfer'
            file_format = 'txt'
            return {
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': (
                    '/web/content/?model=teletransfer&id={0}'
                    '&filename_field={1}'
                    '&field=filecontent&download=true'
                    '&filename={1}.{2}'.format(
                        self.id,
                        file_name,
                        file_format
                    )
                ),
            }

    def cargar_comprobantes(self):
        dominio = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('edi_state', '=', 'sent'),
            ('currency_id', '=', self.currency_id.id),
            ('payment_state', 'in', ['not_paid', 'in_payment', 'partial']),
            ('l10n_latam_document_type_id.internal_type', '=', 'invoice'),
        ]
        if self.cliente == 'E':
            dominio.append(('partner_id', 'in', self.partner_ids.ids))
        if self.tipo_doc == 'E':
            dominio.append(('l10n_latam_document_type_id', 'in', self.document_type_ids.ids))
        if self.fecha == 'E':
            dominio.append(('invoice_date', '>=', self.fecha_inicial))
            dominio.append(('invoice_date', '<=', self.fecha_final))
        if self.sin_teletransfer:
            dominio.append(('teletransfer', '=', False))
        move_ids = self.env['account.move'].search(dominio)
        line_ids = []
        for move_id in move_ids:
            line_ids.append((0, 0, {
                'move_id': move_id.id,
                'amount_total_signed': move_id.amount_total_signed,
            }))
        self.write({'line_ids': line_ids})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'teletransfer',
            'res_id': self.id,
            'view_ids': [(False, 'form')],
            'view_mode': 'form',
            'target': 'new',
            'name': 'Teletransfer',
        }

    def caracteres_especiales(self, nombre):
        return nombre.replace('ñ', 'N').\
                      replace('Ñ', 'N').\
                      replace('SOCIEDAD ANONIMA CERRADA', 'S.A.C.').\
                      replace('SOCIEDAD COMERCIAL DE RESPONSABILIDADA LIMITADA', 'S.R.L.').\
                      replace('EMPRESA INDIVIDUAL DE RESPONSABILIDAD LIMITADA', 'E.I.R.L.').\
                      replace("'", '').\
                      replace("Á", 'A').\
                      replace("É", 'E').\
                      replace("Í", 'I').\
                      replace("Ó", 'O').\
                      replace("Ú", 'U')[:40].upper()

    def my_round(self, n, ndigits):
        part = n * 10 ** ndigits
        delta = part - int(part)
        if delta >= 0.5 or -0.5 < delta <= 0:
            part = math.ceil(part)
        else:
            part = math.floor(part)
        return part / (10 ** ndigits)


class TeletransferLine(models.TransientModel):
    _name = 'teletransfer.line'
    _description = 'Teletransfer detalle'

    teletransfer_id = fields.Many2one(
        comodel_name='teletransfer',
        string='Teletransfer',
    )
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Comprobante',
    )
    invoice_partner_display_name = fields.Char(
        string='Cliente',
        related='move_id.invoice_partner_display_name'
    )
    invoice_date = fields.Date(
        string='Fecha de comprobante',
        related='move_id.invoice_date',
    )
    invoice_date_due = fields.Date(
        string='Fecha de vencimiento',
        related='move_id.invoice_date_due',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='move_id.currency_id',
        string='Moneda',
    )
    amount_total_signed = fields.Monetary(string='Total')
    tipo = fields.Selection(selection=[
        ('A', 'Agregar'),
        ('M', 'Modificar'),
        ('E', 'Eliminar'),
    ], string='Tipo', default='A')

    @api.onchange('move_id')
    def _onchange_move_id(self):
        self.amount_total_signed = 0
        if self.move_id:
            self.amount_total_signed = self.move_id.amount_total_signed
