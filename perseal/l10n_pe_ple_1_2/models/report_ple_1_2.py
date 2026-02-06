# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64


class ReportPle0102(models.Model):
    _name = 'report.ple.01.2'
    _inherit = ['report.ple']
    _description = 'Libro de caja y bancos - Detalle de los movimientos de la cuenta corriente'

    line_ids = fields.One2many(comodel_name='report.ple.01.2.line', inverse_name='ple_id', string='Detalle del libro',
                               readonly=True)

    @api.model
    def create(self, vals):
        res = super(ReportPle0102, self).create(vals)
        res.update({'name': self.env['ir.sequence'].next_by_code(self._name)})
        return res

    def action_generate(self):
        prefix = "LE"
        company_vat = self.env.user.company_id.partner_id.vat or ''
        date_start = self.date_from
        year, month = str(fields.Date().from_string(date_start).year), str(
            fields.Date().from_string(date_start).month).rjust(2, "0")
        currency = 2 if self.currency_id.name in ['USD'] else 1  # USD=2 /PEN=1

        account_type_bank = self.env.ref('account.data_account_type_liquidity')
        template = "{}{}{}{}00{}00{}{}{}{}.txt"
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', 'in', ['posted']),
            ('move_id.journal_id.type', '=', 'bank'),
            ('account_id.user_type_id', '=', account_type_bank.id),
            ('company_id', '=', self.company_id.id),
        ]
        moves_obj = self.env['account.move.line'].search(domain, order='date asc, create_date asc')
        self.create_lines(moves_obj)
        if self.type_report in ['normal']:
            # purchase report normal 050200
            data = self._get_content(self.line_ids, year, month)
            filename = template.format(
                prefix, company_vat, year, month, '010200', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}

        self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            self.env['report.ple.01.2.line'].create({
                'move_line_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.move_id.l10n_pe_operation_type_sunat, x)
            })

    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        template = '{period}|{cuo}|{move_name}|{code_bank}|{account_bank}|{fecha_operacion}|' \
                   '{medio_pago}|{glosa}|{partner_document_type}|{partner_document_number}|' \
                   '{partner_name}|{num_transaccion_bancaria}|{movimientos_debe}|{movimientos_haber}|' \
                   '{estado_operacion}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                code_bank=line.code_bank or 99,
                account_bank=line.account_bank,
                fecha_operacion=format_date(line.fecha_operacion),
                medio_pago=line.medio_pago or 999,
                glosa=(line.glosa or '')[:200],
                partner_document_type=line.partner_document_type,
                partner_document_number=line.partner_document_number,
                partner_name=line.partner_name,
                num_transaccion_bancaria=(line.num_transaccion_bancaria or ''),
                movimientos_debe=format(line.movimientos_debe, ".2f"),
                movimientos_haber=format(line.movimientos_haber, ".2f"),
                estado_operacion=line.state_opportunity or '',
            )
        return data


class ReportPle0101Line(models.Model):
    _name = 'report.ple.01.2.line'
    _order = 'fecha_contable'
    _description = 'lineas libro de caja y bancos - Detalle de los movimientos de la cuenta corriente'

    move_line_id = fields.Many2one(comodel_name='account.move.line', string='Apunte')
    codigo_cuenta_desagregado_id = fields.Many2one("account.account", string="Código cuenta contable desagregado", compute='_compute_data')
    journal_id = fields.Many2one('account.journal', string="Diario", compute='_compute_data')

    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento', compute='_compute_data')
    code_bank = fields.Char(string='Codigo entidad financiera')
    account_bank = fields.Char(string='Cuenta entidad financiera', help='Código de la cuenta bancaria del contribuyente')
    fecha_operacion = fields.Date(string="Fecha de la operación", compute='_compute_data')
    medio_pago = fields.Char(string="Medio de Pago")
    glosa = fields.Char(string="Glosa o descripción naturaleza de operación", compute='_compute_data', readonly=False)
    partner_document_type = fields.Char(string='Tipo Documento', compute='_compute_data')
    partner_document_number = fields.Char(string='Nro Documento', compute='_compute_data')
    partner_name = fields.Char(string='Proveedor', compute='_compute_data')
    num_transaccion_bancaria = fields.Char(string="Número Comprobante de Pago", compute='_compute_data')
    movimientos_debe = fields.Float(string="Movimientos del Debe", compute='_compute_data')
    movimientos_haber = fields.Float(string="Movimientos del Haber", compute='_compute_data')
    state_opportunity = fields.Char(string='Estado', compute='_compute_data')

    fecha_contable = fields.Date(string="Fecha Contable", compute='_compute_data')
    ple_id = fields.Many2one(comodel_name='report.ple.01.2')

    @api.depends('move_line_id')
    def _compute_data(self):
        def get_series_correlative(move_line_id):
            if move_line_id.move_id.move_type in ['in_invoice', 'in_refund', 'entry']:
                name = move_line_id.move_id.ref

            elif move_line_id.move_id.move_type in ['out_invoice', 'out_refund']:
                name = move_line_id.move_id.name

            elif move_line_id.move_id.move_type == 'entry':
                name = move_line_id.move_id.statement_id.name
            return name

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        def get_exhange(inv):
            # exch = self.env['res.currency.rate'].search([('currency_id','=',inv.currency_id.id), ('name','=',inv.invoice_date)])
            curren = self.env['res.currency'].search([('name', '=', 'USD')])
            date = inv.invoice_date
            if inv.move_type == 'out_refund':
                if inv.reversed_entry_id.invoice_date:
                    date = inv.reversed_entry_id.invoice_date
            if curren:
                balance = curren._get_conversion_rate(curren, inv.company_currency_id, inv.company_id, date)
            else:
                balance = 1
            # balance = inv.rate_exchange
            return balance

        def get_year_month(date):
            # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
            return '{}{}'.format(str(fields.Date().from_string(date).year),
                                 str(fields.Date().from_string(date).month).rjust(2, "0"))

        def get_state(date, date_from, date_to):
            v_state = '1'  # Por defecto
            if date >= date_from and date <= date_to:
                v_state = '1'
            else:
                v_state = '8'
            return v_state

        def get_partner(move_line_id):
            if move_line_id.move_id.move_type == 'entry':
                partner_id = move_line_id.partner_id
            else:
                partner_id = move_line_id.move_id.payment_id.partner_id
            return partner_id

        # Funcionalidad que valida que la cadena de texto solo tenga alfabeto / numero y demas es guion
        def validate_number_letter(in_str_text_number):
            out_str_text_number = ''
            if in_str_text_number:
                v_data_str = str(in_str_text_number).upper()  # Convertimos en mayusculas
                indice = 0
                while indice < len(v_data_str):
                    # Validamos que el caracter sea alfabeto o es numerico
                    if v_data_str[indice].isalpha() or v_data_str[indice].isdigit():
                        out_str_text_number = out_str_text_number + v_data_str[indice]
                    else:
                        out_str_text_number = out_str_text_number + '-'  # Otro Caracter pasa a ser guion
                    indice += 1

            return out_str_text_number

        def _compute_campo_m_correlativo_asiento_contable(move_line_id, move_id):
            indice = sorted([(line.account_id.code, line.id) for line in move_id.line_ids]).index(
                (move_line_id.account_id.code, move_line_id.id))
            return u'{}{}'.format(move_id.l10n_pe_operation_type_sunat, indice)

        self.mapped(lambda x: x.update({
            'journal_id': x.move_line_id.move_id.journal_id.id,
            'period': '{}00'.format(get_year_month(x.move_line_id.date)),
            'cuo': validate_number_letter(x.move_line_id.move_id.name),
            'move_name': _compute_campo_m_correlativo_asiento_contable(x.move_line_id, x.move_line_id.move_id),
            'code_bank': x.move_line_id.move_id.journal_id.bank_id.bic,
            'codigo_cuenta_desagregado_id': x.move_line_id.account_id.id,
            'account_bank': x.move_line_id.move_id.journal_id.bank_account_id.acc_number,
            'fecha_operacion': x.move_line_id.move_id.invoice_date or x.move_line_id.date or False,
            'medio_pago': x.move_line_id.move_id.journal_id.medium_payment,
            'glosa': x.move_line_id.name or "-",
            'partner_document_type': get_partner(x.move_line_id).l10n_latam_identification_type_id.l10n_pe_vat_code or '',
            'partner_document_number': get_partner(x.move_line_id).vat or '',
            'partner_name': get_partner(x.move_line_id).name or '',
            'num_transaccion_bancaria': get_series_correlative(x.move_line_id),
            'movimientos_debe': x.move_line_id.debit,
            'movimientos_haber': x.move_line_id.credit,
            'state_opportunity': get_state(x.move_line_id.date, x.ple_id.date_from, x.ple_id.date_to),
            'fecha_contable': x.move_line_id.date or x.move_line_id.move_id.date or False,
        }))

    def _l10n_pe_edi_get_edi_values(self, invoice):

        def format_float(amount, precision=2):
            ''' Helper to format monetary amount as a string with 2 decimal places. '''
            if amount is None or amount is False:
                return None
            return '%.*f' % (precision, amount)

        def unit_amount(amount, quantity):
            ''' Helper to divide amount by quantity by taking care about float division by zero. '''
            if quantity:
                return invoice.currency_id.round(amount / quantity)
            else:
                return 0.0

        values = {
            'record': invoice,
            'spot': invoice._l10n_pe_edi_get_spot(),
            'PaymentMeansID': invoice._l10n_pe_edi_get_payment_means(),
            'invoice_lines_vals': [],
            'certificate_date': self.env['l10n_pe_edi.certificate']._get_pe_current_datetime().date(),
            'format_float': format_float,
            'tax_details': {
                'total_excluded': 0.0,
                'total_included': 0.0,
                'total_taxes': 0.0,
            },
        }
        tax_details = values['tax_details']

        # Invoice lines.
        tax_res_grouped = {}
        invoice_lines = invoice.invoice_line_ids.filtered(lambda line: not line.display_type)
        for i, line in enumerate(invoice_lines, start=1):
            price_unit_wo_discount = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)

            taxes_res = line.tax_ids.compute_all(
                price_unit_wo_discount,
                currency=line.currency_id,
                quantity=line.quantity,
                product=line.product_id,
                partner=line.partner_id,
                is_refund=invoice.move_type in ('out_refund', 'in_refund'),
            )

            taxes_res.update({
                'unit_total_included': unit_amount(taxes_res['total_included'], line.quantity),
                'unit_total_excluded': unit_amount(taxes_res['total_excluded'], line.quantity),
                'price_unit_type_code': '01' if not line.currency_id.is_zero(price_unit_wo_discount) else '02',
            })
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                tax_res.update({
                    'tax_amount': tax.amount,
                    'tax_amount_type': tax.amount_type,
                    'price_unit_type_code': '01' if not line.currency_id.is_zero(tax_res['amount']) else '02',
                    'l10n_pe_edi_tax_code': tax.l10n_pe_edi_tax_code,
                    'l10n_pe_edi_group_code': tax.tax_group_id.l10n_pe_edi_code,
                    'l10n_pe_edi_international_code': tax.l10n_pe_edi_international_code,
                })

                tuple_key = (
                    tax_res['l10n_pe_edi_group_code'],
                    tax_res['l10n_pe_edi_international_code'],
                    tax_res['l10n_pe_edi_tax_code'],
                )

                tax_res_grouped.setdefault(tuple_key, {
                    'base': 0.0,
                    'amount': 0.0,
                    'l10n_pe_edi_group_code': tax_res['l10n_pe_edi_group_code'],
                    'l10n_pe_edi_international_code': tax_res['l10n_pe_edi_international_code'],
                    'l10n_pe_edi_tax_code': tax_res['l10n_pe_edi_tax_code'],
                })
                tax_res_grouped[tuple_key]['base'] += tax_res['base']
                tax_res_grouped[tuple_key]['amount'] += tax_res['amount']

                tax_details['total_excluded'] += tax_res['base']
                tax_details['total_included'] += tax_res['base'] + tax_res['amount']
                tax_details['total_taxes'] += tax_res['amount']

                values['invoice_lines_vals'].append({
                    'index': i,
                    'line': line,
                    'tax_details': taxes_res,
                })

        values['tax_details']['grouped_taxes'] = list(tax_res_grouped.values())

        return values
