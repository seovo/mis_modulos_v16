# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class ReportPle08(models.Model):
    _name = 'report.ple.08.3'
    _inherit = ['report.ple']
    _description = 'Registro de Compras simplificado'

    # file_non_domiciled = fields.Binary(string='Archivo TXT no domiciliado', readonly=True)
    # filename_non_domiciled = fields.Char(string='Nombre del archivo no simplificado')
    #
    # file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    # filename_simplified = fields.Char(string='Nombre del archivo simplificado')
    line_ids = fields.One2many(comodel_name='report.ple.08.3.line', inverse_name='ple_id', string='Detalle del libro',
                               readonly=True)

    @api.model
    def create(self, vals):
        res = super(ReportPle08, self).create(vals)
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
            ('state', 'in', ['posted']),
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['in_invoice', 'in_refund'])
        ]
        invoice_obj = self.env['account.move'].search(domain, order='date asc, create_date asc')
        self.create_lines(invoice_obj)
        if self.type_report in ['normal']:
            # purchase report normal
            data = self._get_content(self.line_ids, year, month)
            filename = template.format(
                prefix, company_vat, year, month, '080300', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}

            # # purchase report non-domiciled
            # data = self._get_content_non_domiciled(
            #     self.line_ids)  # Esto no se usara pero debemos generar el archivo con 01 linea
            # filename = template.format(
            #     prefix, company_vat, year, month, '080200', self.indicator_operation,
            #     0, currency,
            #     1)  # self.indicator_content, currency, 1) #No debe tener contenido pues el archivo es en blanco
            # value.update(
            #     {'filename_non_domiciled': filename, 'file_non_domiciled': base64.encodebytes(data.encode('utf-8'))})
        self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            self.env['report.ple.08.3.line'].create({
                'invoice_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.l10n_pe_operation_type_sunat, x)
            })

    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{date_due}|{document_payment_type}|' \
                   '{document_payment_series}|{document_payment_number}|' \
                   '{no_fiscal_credit}|{supplier_document_type}|{supplier_document_number}|' \
                   '{supplier_name}|{amount_untaxed1}|{amount_tax_igv1}|' \
                   '{amount_tax_plastic_bag}|{amount_tax_other}|{amount_total}|' \
                   '{currency}|{exchange_currency}|{date_emission_update}|{document_payment_type_update}|' \
                   '{document_payment_series_update}|{document_payment_correlative_update}|' \
                   '{date_detraction}|{number_detraction}|{retention_mark}|{goods_services_classification}|' \
                   '{type_error_1}|{type_error_2}|{type_error_3}|' \
                   '{method_payment}|{state_opportunity}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                date_due=line.date_due or '',
                document_payment_type=line.document_payment_type or '',
                document_payment_series=line.document_payment_series or '',
                date_dua=line.date_dua,
                document_payment_number=line.document_payment_number or '',
                no_fiscal_credit=line.no_fiscal_credit or '',
                supplier_document_type=line.supplier_document_type or '',
                supplier_document_number=line.supplier_document_number or '',
                supplier_name=line.supplier_name or '',
                amount_untaxed1=round(line.amount_untaxed1, 2) or '0.00',
                amount_tax_igv1=round(line.amount_tax_igv1, 2) or '0.00',
                amount_untaxed2=round(line.amount_untaxed2, 2) or '0.00',
                amount_tax_igv2=round(line.amount_tax_igv2, 2) or '0.00',
                amount_untaxed3=round(line.amount_untaxed3, 2) or '0.00',
                amount_tax_igv3=round(line.amount_tax_igv3, 2) or '0.00',
                amount_exo=round(line.amount_exo, 2) or '0.00',
                amount_tax_isc=round(line.amount_tax_isc, 2) or '0.00',
                amount_tax_plastic_bag=round(line.amount_tax_plastic_bag, 2) or '0.00',
                amount_tax_other=round(line.amount_tax_other, 2) or '0.00',
                amount_total=round(line.amount_total, 2) or '0.00',
                currency=line.currency or '',
                exchange_currency=str(format(line.exchange_currency, '.3f')) or '0.000',
                date_emission_update=line.date_emission_update or '',
                document_payment_type_update=line.document_payment_type_update or '',
                document_payment_series_update=line.document_payment_series_update or '',
                dua_code=line.dua_code or '',
                document_payment_correlative_update=line.document_payment_correlative_update or '',
                date_detraction=line.date_detraction or '',
                number_detraction=line.number_detraction or '',
                retention_mark=line.retention_mark or '',
                goods_services_classification=line.goods_services_classification or '',
                contract_ident=line.contract_ident or '',
                type_error_1=line.type_error_1 or '',
                type_error_2=line.type_error_2 or '',
                type_error_3=line.type_error_3 or '',
                type_error_4=line.type_error_4 or '',
                method_payment=line.method_payment and '1' or '',
                state_opportunity=line.state_opportunity or ''
            )
        return data


class ReportPle08Line(models.Model):
    _name = 'report.ple.08.3.line'
    _order = 'date_emission,supplier_document_number,amount_total'
    _description = 'Detalle de registro de compras'

    invoice_id = fields.Many2one(comodel_name='account.move', string='Factura')
    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento')
    date_emission = fields.Char(string='Fecha de emisión', compute='_compute_data')
    date_due = fields.Char(string='Fecha de vencimiento', compute='_compute_data')
    document_payment_type = fields.Char(string='Tipo', compute='_compute_data')
    document_payment_series = fields.Char(string='Serie', compute='_compute_data')
    document_payment_number = fields.Char(string='Nro del comprobante', compute='_compute_data')
    no_fiscal_credit = fields.Float(string='Operaciones sin derecho fiscal')
    supplier_document_type = fields.Char(string='Tipo Documento', compute='_compute_data')
    supplier_document_number = fields.Char(string='Nro Documento', compute='_compute_data')
    supplier_name = fields.Char(string='Proveedor', compute='_compute_data')
    amount_untaxed1 = fields.Float(string='Base imponible', compute='_compute_amount', digits=(12, 2))
    amount_tax_igv1 = fields.Float(string='IGV y/o IPM', compute='_compute_amount', digits=(12, 2))
    amount_tax_plastic_bag = fields.Float(string='Impuesto Bolsa de Plástico', compute='_compute_amount',
                                          digits=(12, 2))
    amount_tax_other = fields.Float(string='Otros conceptos', compute='_compute_amount', digits=(12, 2))
    amount_total = fields.Float(string='Importe Total', compute='_compute_amount', digits=(12, 2))
    currency = fields.Char(string='Moneda', compute='_compute_data')
    exchange_currency = fields.Float(string='Tipo de cambio', compute='_compute_data', digits=(10, 3))
    date_emission_update = fields.Char(string='Fecha emision de CR', compute='_compute_data')
    document_payment_type_update = fields.Char(string='Tipo de CR', compute='_compute_data')
    document_payment_series_update = fields.Char(string='Serie de CR', compute='_compute_data')
    document_payment_correlative_update = fields.Char(string='Nro de CR')
    date_detraction = fields.Char(string='Fecha de detracción', compute='_compute_data')
    number_detraction = fields.Char(string='Constancia de depósito de detracción')
    retention_mark = fields.Char(string='Pago sujeto a retención')
    goods_services_classification = fields.Char(string='Clasificación de los bienes y servicios')
    type_error_1 = fields.Char(string='Error tipo 1')
    type_error_2 = fields.Char(string='Error tipo 2')
    type_error_3 = fields.Char(string='Error tipo 3')
    method_payment = fields.Boolean(string='Método de pago', compute='_compute_data')
    state_opportunity = fields.Char(string='Estado', compute='_compute_data')
    ple_id = fields.Many2one(comodel_name='report.ple.08.3')

    date_dua = fields.Integer(string='Año de emisión de la DUA', compute='_compute_data')  ####
    amount_untaxed2 = fields.Float(string='Base imponible 2', compute='_compute_amount', digits=(12, 2))  ####
    amount_tax_igv2 = fields.Float(string='IGV y/o IPM 2', compute='_compute_amount', digits=(12, 2))  ####
    amount_untaxed3 = fields.Float(string='Base imponible 3', compute='_compute_amount', digits=(12, 2))  ####
    amount_tax_igv3 = fields.Float(string='IGV y/o IPM 3', compute='_compute_amount', digits=(12, 2))  ####
    amount_exo = fields.Float(string='Exonerado', compute='_compute_amount', digits=(12, 2))  ####
    amount_tax_isc = fields.Float(string='ISC', compute='_compute_amount', digits=(12, 2))  ####
    dua_code = fields.Char(string='Codigo DUA')  ####
    contract_ident = fields.Char(string='Identificación del contrato')  ####
    type_error_4 = fields.Char(string='Error tipo 4')  ####

    @api.depends('invoice_id')
    def _compute_data(self):
        def get_series_correlative(name):
            return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')

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

        def get_detraction(invoice):
            number, date = False, False
            if invoice.payment_state in ['paid', 'in_payment'] and invoice.state == 'posted' and invoice.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']:
                if invoice.fields_get().get('detraction_show', False):
                    payment = self.env['account.payment'].search([('ref', '=', invoice.name), ('is_detraction_pay', '=', True)], limit=1)
                    if invoice.id in payment.reconciled_bill_ids.ids and payment:
                        number, date = payment.detraction_operation_number, payment.detraction_operation_date
            detraccion = [number, date]
            return detraccion

        def get_year_month(date):
            # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
            return '{}{}'.format(str(fields.Date().from_string(date).year),
                                 str(fields.Date().from_string(date).month).rjust(2, "0"))

        def get_state(in_date_emission, in_date_account, in_number_igv):
            v_state = '6'  # Por defecto (dentro de los 12 meses)
            if '{}00'.format(get_year_month(in_date_emission)) == '{}00'.format(get_year_month(in_date_account)):
                if in_number_igv <= 0.00:  # El comprobante no da derecho al credito fiscal
                    v_state = '0'
                else:  # Si da derecho al credito fiscal
                    v_state = '1'
            else:
                v_dif = in_date_account - in_date_emission
                diferencia = abs(v_dif.days)
                if diferencia > 365:
                    v_state = '7'
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

        self.mapped(lambda x: x.update({
            'period': '{}00'.format(get_year_month(x.invoice_id.date)),
            'cuo': validate_number_letter(x.invoice_id.name),
            'date_emission': format_date(x.invoice_id.invoice_date),
            'date_due': format_date(x.invoice_id.invoice_date),  # format_date(x.invoice_id.invoice_date_due) or '',
            'document_payment_type': x.invoice_id.l10n_latam_document_type_id.code or '',
            'document_payment_series': get_series_correlative(x.invoice_id.l10n_latam_document_number)[0],
            'date_dua': 0,  # fields.Date().from_string(x.invoice_id.date_invoice).year,
            'document_payment_number': get_series_correlative(x.invoice_id.l10n_latam_document_number)[1],
            'supplier_document_type': x.invoice_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
            'supplier_document_number': x.invoice_id.partner_id.vat or '',
            'supplier_name': x.invoice_id.partner_id.name or '',
            'date_emission_update':
                (x.invoice_id.move_type == 'in_refund' and format_date(x.invoice_id.reversed_entry_id.invoice_date) or
                 format_date(x.invoice_id.reversed_entry_id.invoice_date)),
            'document_payment_type_update':
                (
                            x.invoice_id.move_type == 'in_refund' and x.invoice_id.reversed_entry_id.l10n_latam_document_type_id.code or
                            x.invoice_id.reversed_entry_id.l10n_latam_document_type_id.code) or '',
            'document_payment_series_update':
                (x.invoice_id.move_type == 'in_refund' and get_series_correlative(x.invoice_id.reversed_entry_id.ref)[
                    0] or
                 get_series_correlative(x.invoice_id.reversed_entry_id.ref)[0]),
            'document_payment_correlative_update':
                (x.invoice_id.move_type == 'in_refund' and get_series_correlative(x.invoice_id.reversed_entry_id.ref)[
                    1] or
                 get_series_correlative(x.invoice_id.reversed_entry_id.ref)[1]),
            'currency': x.invoice_id.currency_id.name or '',
            'exchange_currency': get_exhange(x.invoice_id),
            'date_detraction': format_date(get_detraction(x.invoice_id)[1]) or '',
            'number_detraction': get_detraction(x.invoice_id)[0] or '',
            # 'date_detraction': format_date(x.invoice_id.date_payment_detraction),
            # 'number_detraction': x.invoice_id.constance_payment_detraction or '',
            'retention_mark': '',
            'goods_services_classification': '',
            'contract_ident': '',
            'type_error_1': '',
            'type_error_2': '',
            'type_error_3': '',
            'type_error_4': '',
            'dua_code': '',
            'state_opportunity': get_state(x.invoice_id.invoice_date, x.invoice_id.date, x.invoice_id.amount_tax),
            'method_payment': x.invoice_id.state in ['paid'] or False
        }))

    @api.depends('invoice_id')
    def _compute_amount(self):

        def get_amount_tax(invoice):
            def compute_tax(p, t, x):
                res = t.compute_all(p, x.invoice_id.currency_id, x.quantity, product=x.product_id,
                                    partner=x.invoice_id.partner_id)
                return res['total_included'] - res['total_excluded']

            data_process = self._l10n_pe_edi_get_edi_values(invoice)
            v_base_imponible = 0
            v_monto_exo = 0
            totalVentaGravada = 0
            totalVentaExonerada = 0
            totalVentaInafecta = 0
            sumatoriaIgv = 0
            isc = 0
            other = 0
            amount_total = invoice.amount_total

            v_base_imponible = round(data_process['tax_details']['total_excluded'], 2)
            igv = round(data_process['tax_details']['total_taxes'], 2)

            for element in data_process['tax_details']['grouped_taxes']:
                if element.get('l10n_pe_edi_tax_code') == '1000':
                    totalVentaGravada += element.get('base')
                    sumatoriaIgv += element.get('amount')
                if element.get('l10n_pe_edi_tax_code') == '9997':
                    totalVentaExonerada += element.get('base')
                if element.get('l10n_pe_edi_tax_code') == '9998':
                    totalVentaInafecta += element.get('base')

            if invoice.move_type == 'in_refund':
                v_base_imponible = v_base_imponible * -1
                igv = igv * -1
                totalVentaGravada = totalVentaGravada * -1
                totalVentaExonerada = totalVentaExonerada * -1
                totalVentaInafecta = totalVentaInafecta * -1
                isc = isc * -1
                other = other * -1
                amount_total = amount_total * -1

            if invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.invoice_date
                if invoice.move_type == 'in_refund':
                    date = invoice.reversed_entry_id.invoice_date
                v_base_imponible = invoice.currency_id._convert(v_base_imponible, invoice.company_id.currency_id,
                                                                invoice.company_id, date)
                igv = invoice.currency_id._convert(igv, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaGravada = invoice.currency_id._convert(totalVentaGravada, invoice.company_id.currency_id,
                                                                 invoice.company_id, date)
                totalVentaExonerada = invoice.currency_id._convert(totalVentaExonerada, invoice.company_id.currency_id,
                                                                   invoice.company_id, date)
                totalVentaInafecta = invoice.currency_id._convert(totalVentaInafecta, invoice.company_id.currency_id,
                                                                  invoice.company_id, date)
                isc = invoice.currency_id._convert(isc, invoice.company_id.currency_id, invoice.company_id, date)
                other = invoice.currency_id._convert(other, invoice.company_id.currency_id, invoice.company_id, date)
                amount_total = invoice.currency_id._convert(amount_total, invoice.company_id.currency_id,
                                                            invoice.company_id, date)
                # exo = exo + v_monto_exo
            return v_base_imponible, igv, totalVentaGravada, totalVentaExonerada, totalVentaInafecta, isc, other, amount_total

        def get_invoice_tax(lines_tax):
            # usamos el impuesto asignado al account_invoice
            igv = exo = inaf = rice = isc = other = 0
            for invtax in lines_tax:
                if invtax.tax_id.tax_sunat.code in ['1000']:
                    igv = igv + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['9997']:
                    exo = exo + invtax.base
                if invtax.tax_id.tax_sunat.code in ['9998']:
                    inaf = inaf + invtax.base
                if invtax.tax_id.tax_sunat.code in ['1016']:
                    rice = rice + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['2000']:
                    isc = isc + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['9999']:
                    other = other + invtax.amount
            return igv, exo, inaf, rice, isc, other

        self.mapped(lambda w: w.update({
            'amount_untaxed1': get_amount_tax(w.invoice_id)[0],
            'amount_tax_igv1': get_amount_tax(w.invoice_id)[1],
            'amount_untaxed2': 0,
            'amount_tax_igv2': 0,
            'amount_untaxed3': 0,
            'amount_tax_igv3': 0,
            'amount_exo': (get_amount_tax(w.invoice_id)[3] + get_amount_tax(w.invoice_id)[4]),
            'amount_tax_isc': get_amount_tax(w.invoice_id)[5],
            'amount_tax_plastic_bag': 0,
            'amount_tax_other': get_amount_tax(w.invoice_id)[6],
            'amount_total': get_amount_tax(w.invoice_id)[7]
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
