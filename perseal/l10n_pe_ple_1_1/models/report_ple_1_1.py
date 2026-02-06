# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class ReportPle0101(models.Model):
    _name = 'report.ple.01.1'
    _inherit = ['report.ple']
    _description = 'Registro Diario'

    # file_non_domiciled = fields.Binary(string='Archivo TXT no domiciliado', readonly=True)
    # filename_non_domiciled = fields.Char(string='Nombre del archivo no simplificado')
    #
    # file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    # filename_simplified = fields.Char(string='Nombre del archivo simplificado')
    line_ids = fields.One2many(comodel_name='report.ple.01.1.line', inverse_name='ple_id', string='Detalle del libro',
                               readonly=True)

    @api.model
    def create(self, vals):
        res = super(ReportPle0101, self).create(vals)
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

        account_type_cash = self.env.ref('account.data_account_type_liquidity')
        template = "{}{}{}{}00{}00{}{}{}{}.txt"
        # Usamos el tipo de Comprobante = FACTURA DE COMPRA / N/C COMPRA / OTROS SEGUN CONFIG EN EL DIARIO
        # s_args = [
        #     ('date_start', '<=', self.range_id.date_start),
        #     ('date_stop', '>=', self.range_id.date_stop),
        #     ('company_id', '=', self.company_id.id),
        # ]
        # date_period = self.env['account.period'].search(s_args)
        # if not date_period:
        #     raise UserError(_('La Fecha ingresada no tiene PERIODO CONTABLE.'))
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('move_id.state', 'in', ['posted']),
            ('move_id.journal_id.type', '=', 'cash'),
            ('account_id.user_type_id', '=', account_type_cash.id),
            ('company_id', '=', self.company_id.id),
        ]
        moves_obj = self.env['account.move.line'].search(domain, order='date asc, create_date asc')
        self.create_lines(moves_obj)
        if self.type_report in ['normal']:
            # purchase report normal 050200
            data = self._get_content(self.line_ids, year, month)
            filename = template.format(
                prefix, company_vat, year, month, '010100', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}

        self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            self.env['report.ple.01.1.line'].create({
                'move_line_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.move_id.l10n_pe_operation_type_sunat, x)
            })

    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        template = '{period}|{cuo}|{move_name}|{codigo_cuenta}|{codigo_unidad_op}|{codigo_centro_cos}|' \
                   '{tipo_moneda}|{tipo_comprobante_pago}|{num_serie_comprobante_pago}|{num_comprobante_pago}|' \
                   '{fecha_contable}|{fecha_vencimiento}|{fecha_operacion}|{glosa}|' \
                   '{glosa_referencial}|{movimientos_debe}|{movimientos_haber}|' \
                   '{dato_estructurado}|{estado_operacion}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                codigo_cuenta=(line.codigo_cuenta_desagregado or '')[:24] ,
                codigo_unidad_op=(line.codigo_unidad_operacion or '')[:24],
                codigo_centro_cos=(line.codigo_centro_costos or '')[:24],
                tipo_moneda=(line.tipo_moneda_origen or '')[:3],
                tipo_doc_iden_emisor=(line.tipo_doc_iden_emisor or '')[:1],
                num_doc_iden_emisor=(line.num_doc_iden_emisor or '')[:15],
                tipo_comprobante_pago=(line.tipo_comprobante_pago or '')[:2],
                num_serie_comprobante_pago=(line.num_serie_comprobante_pago or '')[:20],
                num_comprobante_pago=(line.num_comprobante_pago or '')[:20],
                fecha_contable=format_date(line.fecha_contable),
                fecha_vencimiento=format_date(line.fecha_vencimiento),
                fecha_operacion=format_date(line.fecha_operacion),
                glosa=(line.glosa or '')[:200],
                glosa_referencial=(line.glosa_referencial or '')[:200],
                movimientos_debe=format(line.movimientos_debe, ".2f"),
                movimientos_haber=format(line.movimientos_haber, ".2f"),
                dato_estructurado=(line.dato_estructurado or '')[:92],
                estado_operacion=line.state_opportunity or '',

            )
        return data


class ReportPle0101Line(models.Model):
    _name = 'report.ple.01.1.line'
    _order = 'fecha_contable'
    _description = 'Detalle de registro diario'

    move_line_id = fields.Many2one(comodel_name='account.move.line', string='Apunte')
    codigo_cuenta_desagregado_id = fields.Many2one("account.account", string="Código cuenta contable desagregado id", compute='_compute_data')
    journal_id = fields.Many2one('account.journal', string="Diario", compute='_compute_data')

    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento', compute='_compute_data')
    codigo_cuenta_desagregado = fields.Char(string="Código cuenta contable desagregado", compute='_compute_data')
    codigo_unidad_operacion = fields.Char(string="Código unidad operación", default="")
    codigo_centro_costos = fields.Char(string="Código centro de costos", default="")
    tipo_moneda_origen = fields.Char(string="Tipo de Moneda de origen", compute='_compute_data', readonly=True)
    tipo_comprobante_pago = fields.Char(string="Tipo de Comprobante Pago", compute='_compute_data', readonly=True)
    num_serie_comprobante_pago = fields.Char(string="Número serie Comprobante Pago", compute='_compute_data')  # , inverse= '_inverse_compute_campo_num_serie_comprobante_pago', store = True , readonly=False )
    num_comprobante_pago = fields.Char(string="Número Comprobante de Pago", compute='_compute_data')  # inverse= '_inverse_compute_campo_num_comprobante_pago' ,store = True ,  readonly=False)
    fecha_contable = fields.Date(string="Fecha Contable", compute='_compute_data')
    fecha_vencimiento = fields.Date(string="Fecha de vencimiento", compute='_compute_data')
    fecha_operacion = fields.Date(string="Fecha de la operación o emisión", compute='_compute_data')
    glosa = fields.Char(string="Glosa o descripción naturaleza de operación", compute='_compute_data', readonly=False)
    glosa_referencial = fields.Char(string="Glosa referencial", default="")
    movimientos_debe = fields.Float(string="Movimientos del Debe", compute='_compute_data')
    movimientos_haber = fields.Float(string="Movimientos del Haber", compute='_compute_data')
    dato_estructurado = fields.Char(string="Dato estructurado")  # , compute='_compute_campo_dato_estructurado')
    state_opportunity = fields.Char(string='Estado', compute='_compute_data')
    ple_id = fields.Many2one(comodel_name='report.ple.01.1')
    tipo_doc_iden_emisor = fields.Char(string="Tipo Documento Identidad Emisor",
                                       compute='_compute_data',
                                       readonly=True)
    num_doc_iden_emisor = fields.Char(string="Número Documento Identidad Emisor",
                                      compute='_compute_data',
                                      readonly=True)

    @api.depends('move_line_id')
    def _compute_data(self):
        def get_series_correlative(move_line_id):
            if move_line_id.move_id.move_type in ['in_invoice', 'in_refund', 'entry']:
                name = move_line_id.move_id.ref
                return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')
            if move_line_id.move_id.move_type in ['out_invoice', 'out_refund']:
                name = move_line_id.move_id.name
                return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')
            return ('','')

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
            'period': '{}00'.format(get_year_month(x.move_line_id.date)),
            'move_name': _compute_campo_m_correlativo_asiento_contable(x.move_line_id, x.move_line_id.move_id),
            'cuo': validate_number_letter(x.move_line_id.name),
            'codigo_cuenta_desagregado_id': x.move_line_id.account_id.id,
            'codigo_cuenta_desagregado': x.move_line_id.account_id.code,
            'journal_id': x.move_line_id.move_id.journal_id.id,
            'tipo_moneda_origen': x.move_line_id.currency_id.name,
            'tipo_doc_iden_emisor': x.move_line_id.move_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or
                                    x.move_line_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or "",
            'num_doc_iden_emisor': x.move_line_id.move_id.partner_id.vat or x.move_line_id.partner_id.vat or "",
            'tipo_comprobante_pago':x.move_line_id.move_id.l10n_latam_document_type_id.code or '00',
            'num_serie_comprobante_pago': get_series_correlative(x.move_line_id)[0],
            'num_comprobante_pago': get_series_correlative(x.move_line_id)[1],
            'fecha_contable':x.move_line_id.date or x.move_line_id.move_id.date or False,
            'fecha_vencimiento':x.move_line_id.date_maturity or False,
            'fecha_operacion' : x.move_line_id.move_id.date or x.move_line_id.date or False,
            'glosa': x.move_line_id.name or "-",
            'movimientos_debe':x.move_line_id.debit,
            'movimientos_haber': x.move_line_id.credit,
            'state_opportunity': get_state(x.move_line_id.date, x.ple_id.date_from, x.ple_id.date_to),

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
