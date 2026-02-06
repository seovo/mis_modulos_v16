# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class ReportPle08(models.Model):
    _name = 'report.ple.08.2'
    _description = 'report ple 8.2'
    _inherit = ['report.ple']
    _description = 'Registro de Compras No domiciliado'

    # file_non_domiciled = fields.Binary(string='Archivo TXT no domiciliado', readonly=True)
    # filename_non_domiciled = fields.Char(string='Nombre del archivo no simplificado')
    #
    # file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    # filename_simplified = fields.Char(string='Nombre del archivo simplificado')
    line_ids = fields.One2many(comodel_name='report.ple.08.2.line', inverse_name='ple_id', string='Detalle del libro',
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
        config_settings = self.env['ple.configuration'].search([('report_type', '=', '8.1'), ('company_id', '=', self.company_id.id)])
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
            ('no_domiciled', '=', True),
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['in_invoice', 'in_refund'])
        ]
        if config_settings.journals_ids:
            domain += [('journal_id', 'in', config_settings.journals_ids.ids)]
        invoice_obj = self.env['account.move'].search(domain, order='date asc, create_date asc')
        self.create_lines(invoice_obj)
        if self.type_report in ['normal']:
            # purchase report normal

            if self.line_ids:
                data = self._get_content(self.line_ids, year, month)
            else:
                data = ' '
            filename = template.format(
                prefix, company_vat, year, month, '080200', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}
        #
        #
            self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            if not line.partner_id.country_id.code_sunat:
                raise UserError(_('Falta codigo sunat para el pais %s. para el partner %s ' % (line.partner_id.country_id.name, line.partner_id.name)))
            self.env['report.ple.08.2.line'].create({
                'invoice_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.l10n_pe_operation_type_sunat, x)
            })


    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{document_payment_type_5}|{document_payment_series_6}|' \
                   '{document_payment_number_7}|{tax_base_8}|{tax_amount_9}|{total_amount_10}|{type_11}|' \
                   '{sequence_dua_12}|{dua_dsi_year_13}|{reference_dua_tax_14}|{retention_mark_15}|{type_currency_16}|' \
                   '{currency_exchange_rate_17}|{provider_country_18}|{supplier_name_19}|{street_provider_20}|' \
                   '{supplier_doc_number_21}|{tax_identification_beneficiary_22}|{supplier_name_beneficiary_23}|' \
                   '{beneficiary_country_24}|{link_taxpayer_resident_25}|{gross_income_26}|{deduction_capital_27}|{gross_income_28}|' \
                   '{retention_rate_29}|{withheld_tax_30}|{double_taxation_31}|{exemption_applied_32}|' \
                   '{type_rent_33}|{mode_service_provided_34}|{application_art_76_35}|' \
                   '{state_opportunity_36}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,

                document_payment_type_5=line.document_payment_type_5 or '',
                document_payment_series_6=line.document_payment_series_6 or '',
                document_payment_number_7=line.document_payment_number_7 or '',
                tax_base_8=round(line.tax_base_8, 2) or '0.00',
                tax_amount_9=round(line.tax_amount_9, 2) or '0.00',
                total_amount_10=round(line.total_amount_10, 2) or '0.00',
                type_11=line.type_11 or '',
                sequence_dua_12=line.sequence_dua_12 or '',
                dua_dsi_year_13=line.dua_dsi_year_13 or '',
                reference_dua_tax_14=line.reference_dua_tax_14 or '',
                retention_mark_15=line.retention_mark_15 or '',
                type_currency_16=line.type_currency_16 or '',
                currency_exchange_rate_17= line.currency_exchange_rate_17 if line.currency_exchange_rate_17 != 0 else '',
                provider_country_18=line.provider_country_18 or '',
                supplier_name_19=line.supplier_name_19 or '',
                street_provider_20=line.street_provider_20 or '',
                supplier_doc_number_21=line.supplier_doc_number_21 or '',
                tax_identification_beneficiary_22=line.tax_identification_beneficiary_22 or '',
                supplier_name_beneficiary_23=line.supplier_name_beneficiary_23 or '',
                beneficiary_country_24=line.beneficiary_country_24 or '',
                link_taxpayer_resident_25=line.link_taxpayer_resident_25 or '',
                gross_income_26=line.gross_income_26 or '',
                deduction_capital_27=line.deduction_capital_27 or '',
                gross_income_28=line.gross_income_28 or '',
                retention_rate_29=line.retention_rate_29 or '',
                withheld_tax_30=line.withheld_tax_30 or '',
                double_taxation_31=line.double_taxation_31 or '',
                exemption_applied_32=line.exemption_applied_32 or '',
                type_rent_33=line.type_rent_33 or '',
                mode_service_provided_34=line.mode_service_provided_34 or '',
                application_art_76_35=line.application_art_76_35 or '',
                state_opportunity_36=line.state_opportunity_36 or '',
            )
        return data



class ReportPle08Line(models.Model):
    _name = 'report.ple.08.2.line'
    _order = 'date_emission'
    _description = 'Detalle de registro de compras'

    invoice_id = fields.Many2one(comodel_name='account.move', string='Factura')
    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento')
    date_emission = fields.Char(string='Fecha de emisión', compute='_compute_data')
    # date_due = fields.Char(string='Fecha de vencimiento', compute='_compute_data')
    document_payment_type_5 = fields.Char(string='Tipo', compute='_compute_data')
    document_payment_series_6 = fields.Char(string='Serie', compute='_compute_data')
    document_payment_number_7 = fields.Char(string='Numero', compute='_compute_data')

    tax_base_8 = fields.Float("Purchase Total", compute='_compute_amount',
                               help="Valor de las adquisiciones no gravadas")


    tax_amount_9 = fields.Float("Other Purchase", compute='_compute_amount',
                                 help="Otros tributos y cargos que no formen parte de la base imponible.")
    total_amount_10 = fields.Float("Total Amount", compute='_compute_amount',
                                   help="Importe total de las adquisiciones registradas según comprobante de pago.")
    type_11 = fields.Char("Tax Doc. Type",
                          help="Tipo de Comprobante de Pago o Documento que sustenta el crédito fiscal")

    sequence_dua_12 = fields.Char("Tax Doc. Serie", size=20, compute='_compute_data',
                                  help="Serie del comprobante de pago o documento que sustenta el crédito fiscal. En los casos de la Declaración Única de Aduanas (DUA) o de la Declaración Simplificada de Importación (DSI) se consignará el código de la dependencia Aduanera")
    dua_dsi_year_13 = fields.Integer("DUA/DSI (YYYY)",compute='_compute_data',
                                     help="Año de emisión de la DUA o DSI")
    reference_dua_tax_14 = fields.Char("Tax Doc. Number", compute='_compute_data',
                                       help="Número del comprobante de pago o documento o número de orden del formulario físico o virtual donde conste el pago del impuesto, tratándose de la utilización de servicios prestados por no domiciliados u otros, número de la DUA o de la DSI, que sustente el crédito fiscal.")
    retention_mark_15 = fields.Char("Retention Amount",
                                    help="Marca del comprobante de pago sujeto a retención",
                                    compute='_compute_data')
    type_currency_16 = fields.Char("Currency", help="Código de la Moneda")
    currency_exchange_rate_17 = fields.Float("Exchange Rate", digits=(1, 3), compute='_compute_data',
                                             help="Tipo de cambio (3).")
    provider_country_18 = fields.Char("Country", compute='_compute_data')
    supplier_name_19 = fields.Char("Name ", size=200, compute='_compute_data',
                                   help="Apellidos y nombres, denominación o razón social  del proveedor. En caso de personas naturales se debe consignar los datos en el siguiente orden: apellido paterno, apellido materno y nombre completo.")
    street_provider_20 = fields.Char("Address", compute='_compute_data')
    supplier_doc_number_21 = fields.Char("ID Number", size=15, compute='_compute_data',
                                         help="Número de RUC del proveedor o número de documento de Identidad, según corresponda.")
    tax_identification_beneficiary_22 = fields.Char("Identificación fiscal",
                                                    compute='_compute_data')

    supplier_name_beneficiary_23 = fields.Char("Name", size=200, compute='_compute_data',
                                               help="Apellidos y nombres, denominación o razón social  del beneficiario efectivo de los pagos. En caso de personas naturales se debe consignar los datos en el siguiente orden: apellido paterno, apellido materno y nombre completo.")
    beneficiary_country_24 = fields.Char("Pais",compute='_compute_data')
    link_taxpayer_resident_25 = fields.Char("Link Type", compute='_compute_data')
    gross_income_26 = fields.Char("Gross Income", compute='_compute_data')
    deduction_capital_27 = fields.Char("Capital Deduction", compute='_compute_data')
    gross_income_28 = fields.Char("Net rent", compute='_compute_data')
    retention_rate_29 = fields.Char("Retention Rate", compute='_compute_data')
    withheld_tax_30 = fields.Char("Withholding Tax", compute='_compute_data')
    double_taxation_31 = fields.Char("Tax Agreement", compute='_compute_data')
    exemption_applied_32 = fields.Char("Exoneration Applied", compute='_compute_data')
    type_rent_33 = fields.Char("Rent Type", help="Type Rent")
    mode_service_provided_34 = fields.Char("Modality of Service", compute='_compute_data')
    application_art_76_35 = fields.Char("Article 76 Application", compute='_compute_data')

    state_opportunity_36 = fields.Char(string='Estado', compute='_compute_data')
    ple_id = fields.Many2one(comodel_name='report.ple.08.2')

    @api.depends('invoice_id')
    def _compute_data(self):
        def get_series_correlative(name):
            r_name = name.split('-')
            if len(r_name) == 2:
                return r_name
            if len(r_name) == 1:
                return ["",r_name]

            return ["",""]


        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        def get_exhange(inv):
            # exch = self.env['res.currency.rate'].search([('currency_id','=',inv.currency_id.id), ('name','=',inv.invoice_date)])
            if inv.currency_id == inv.company_id.currency_id:
                return False
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
            return round(balance,3)

        def get_year_month(date):
            # return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
            return '{}{}'.format(str(fields.Date().from_string(date).year),
                                 str(fields.Date().from_string(date).month).rjust(2, "0"))

        def get_state(in_date_emission, in_date_account, in_number_igv):
            v_state = '0'  # Por defecto (dentro de los 12 meses)
            if '{}00'.format(get_year_month(in_date_emission)) == '{}00'.format(get_year_month(in_date_account)):
                v_state = '0'
            else:
                v_state = '9'
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
            'document_payment_type_5': x.invoice_id.l10n_latam_document_type_id.code or '',
            'document_payment_series_6': get_series_correlative(x.invoice_id.ref)[0],
            'document_payment_number_7': get_series_correlative(x.invoice_id.ref)[1],
            'type_11':x.invoice_id.l10n_latam_document_type_id.code,
            'sequence_dua_12':x.invoice_id.l10n_pe_fiscal_credit_doc_serie,
            'dua_dsi_year_13':x.invoice_id.l10n_pe_dua_year,
            'retention_mark_15':'',
            'reference_dua_tax_14':x.invoice_id.l10n_pe_fiscal_credit_doc_number,
            'type_currency_16':x.invoice_id.currency_id.name,
            'currency_exchange_rate_17':get_exhange(x.invoice_id),
            'provider_country_18':x.invoice_id.partner_id.country_id.code_sunat,
            'supplier_name_19':x.invoice_id.partner_id.name,
            'street_provider_20':x.invoice_id.partner_id.street,
            'supplier_doc_number_21':x.invoice_id.partner_id.vat,
            'tax_identification_beneficiary_22':x.invoice_id.company_id.vat,
            'supplier_name_beneficiary_23': x.invoice_id.company_id.name,
            'beneficiary_country_24': x.invoice_id.company_id.country_id.code_sunat,
            'link_taxpayer_resident_25': '00',
            'gross_income_26': '',
            'deduction_capital_27' :'',
            'gross_income_28':'',
            'retention_rate_29':'',
            'withheld_tax_30':'',
            'double_taxation_31': x.invoice_id.l10n_pe_tax_agreement.name or '00',
            'exemption_applied_32':'',
            'type_rent_33':x.invoice_id.l10n_pe_income_type.name or '',
            'mode_service_provided_34':'1',
            'application_art_76_35':'',
            'state_opportunity_36':get_state(x.invoice_id.invoice_date, x.invoice_id.date, x.invoice_id.amount_tax),

        }))

    @api.depends('invoice_id')
    def _compute_amount(self):

        def get_amount_tax(invoice):
            def compute_tax(p, t, x):
                res = t.compute_all(p, x.invoice_id.currency_id, x.quantity, product=x.product_id,
                                    partner=x.invoice_id.partner_id)
                return res['total_included'] - res['total_excluded']

            config_settings = self.env['ple.configuration'].search([('report_type', '=', '8.2'), ('company_id', '=', self.ple_id.company_id.id)])
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

            total_no_graved = 0
            total_other = 0

            for lines_inv in invoice.invoice_line_ids:
                for tax in lines_inv.tax_ids:
                    if tax.id in config_settings.l10n_pe_notxbl_vat.ids:
                        total_no_graved += lines_inv.amount_currency

                    if tax.id in config_settings.l10n_pe_purchase_other_tax.ids:
                        total_other += lines_inv.amount_currency

            # v_base_imponible = round(data_process['tax_details']['total_excluded'], 2)
            # igv = round(data_process['tax_details']['total_taxes'], 2)
            #
            # for element in data_process['tax_details']['grouped_taxes']:
            #     if element.get('l10n_pe_edi_tax_code') == '1000':
            #         totalVentaGravada += element.get('base')
            #         sumatoriaIgv += element.get('amount')
            #     if element.get('l10n_pe_edi_tax_code') == '9997':
            #         totalVentaExonerada += element.get('base')
            #     if element.get('l10n_pe_edi_tax_code') == '9998':
            #         totalVentaInafecta += element.get('base')


            return total_no_graved, total_other

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
            'tax_base_8': get_amount_tax(w.invoice_id)[0],
            'tax_amount_9': get_amount_tax(w.invoice_id)[1],
            'total_amount_10': get_amount_tax(w.invoice_id)[0]+get_amount_tax(w.invoice_id)[1],
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
