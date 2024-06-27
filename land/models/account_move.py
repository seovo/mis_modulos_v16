from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
CURRENCY = {
    "PEN": 1,
    "USD": 2,
    "EUR": 3,
    "GBP": 4,
}
from datetime import datetime, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'
    narration_text = fields.Text()

    narration_str = fields.Text(compute="get_narration",store=True)
    bank_origin_ids = fields.One2many('bank.origin','move_id',string="Cuentas Bancarias")
    is_separation_land = fields.Boolean(string="Es una Separación Terreno")
    is_initial_land = fields.Boolean(string="Es Inicial Terreno",compute='get_is_initial_land')
    days_expired_land = fields.Integer()
    value_mora_land = fields.Float(string="Precio Mora", default=10)

    invoice_date_due_separation = fields.Date(
        string='Fecha Vencimiento Separacion',
        compute='_compute_invoice_date_due_separation', store=True, readonly=False,
        states={'draft': [('readonly', False)]},
        index=True,
        copy=False,
    )

    days_max_due_separation = fields.Integer(
        string="Dias Maximo Separación",
        default=15 ,
        states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    mz_land_separation  = fields.Char(string="MZ")
    lot_land_separation = fields.Char(string="Lote")
    sector_land_separation = fields.Char(string="Etapa")
    sale_order_count_store = fields.Integer(related='sale_order_count',store=True)
    days_count_expired_separation = fields.Integer(compute='get_days_count_expired_separation',string="Dias Expirados")
    amount_due_land = fields.Float(compute='get_is_initial_land')
    qty_due_land = fields.Float(compute='get_is_initial_land')
    amount_mora_land = fields.Float(compute='get_is_initial_land')
    report_lot_land_line_id = fields.Many2one('report.lot.land.line', compute='get_report_lot_land_line_id', store=True)



    @api.depends('mz_land_separation', 'lot_land_separation')
    def get_report_lot_land_line_id(self, product_tmp=None):
        for record in self:
            if not product_tmp:
                product_tmp = self.env['product.template'].search(
                    [('company_id', '=', record.company_id.id), ('payment_land_dues', '=', True)])
                if not product_tmp:
                    product_tmp = self.env['product.template'].search(
                        [('payment_land_dues', '=', True), ('attribute_line_ids', '!=', False)])

            line = None
            # raise ValueError(product_tmp)

            if record.mz_land_separation and record.lot_land_separation:
                line = self.env['report.lot.land.line'].search([
                    ('mz_value_id.name', '=', record.mz_land_separation),
                    ('name', '=', str(int(record.lot_land_separation))),
                    ('product_tmp_id', '=', product_tmp.id)
                ])
            record.report_lot_land_line_id = line

    @api.depends('invoice_line_ids','invoice_line_ids.product_id','narration')
    def get_is_initial_land(self):
        for record in self:
            is_initial = False
            amount_mora = 0
            amount_due = 0
            qty_due = 0

            for line in record.invoice_line_ids:
                if line.product_id.is_advanced_land:
                    is_initial = True

                if line.product_id.is_mora_land:
                    amount_mora += line.price_total
                else:
                    qty_due = line.quantity
                    amount_due += line.price_total
            record.qty_due_land = qty_due
            record.is_initial_land = is_initial
            record.amount_due_land = amount_due
            record.amount_mora_land = amount_mora

    def get_days_count_expired_separation(self):
        for record in self:
            diff = None
            if record.invoice_date_due_separation:
                diff = fields.Datetime.now().date() -  record.invoice_date_due_separation
                diff = diff.days
            record.days_count_expired_separation = diff



    def send_notify_separation(self):
        pass


    @api.depends('days_max_due_separation','invoice_date')
    def _compute_invoice_date_due_separation(self):
        for move in self:
            move.invoice_date_due_separation =  move.invoice_date +  timedelta(days=move.days_max_due_separation) if move.invoice_date and move.days_max_due_separation else None



    @api.onchange('is_separation_land','partner_id')
    def change_is_separation_land(self):
        for record in self:
            if record.is_separation_land :
                record.invoice_payment_term_id = self.env.ref('account.account_payment_term_immediate').id

    def create_sale_if_separation(self):

        return {
            "name": f"Cotizacion",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order",
            "target": "current",
            "context": {
                'default_move_separation_land_id': self.id  ,
                'default_partner_id': self.partner_id.id
            }

        }
    @api.model
    def create(self,vals):
        res = super(AccountMove, self).create(vals)


        for record in res:
            for line in record.invoice_line_ids:
                if line.product_id.is_advanced_land:
                    if line.product_id.description_sale:
                        record.narration_text = line.product_id.description_sale


            if record.days_expired_land  and record.days_expired_land != 0 and record.journal_id.id != 10:
                product = self.env['product.product'].search([('is_mora_land','=',True)])
                if not product:
                    raise ValueError('NO SE INDICO PRODUCTO MORA')

                record.invoice_line_ids[0].copy(default={
                    'name': 'Mora' ,
                    'product_id': product.id ,
                    'sale_line_ids': None ,
                    'quantity': record.days_expired_land ,
                    'price_unit': record.value_mora_land,
                    'move_id': record.id
                    #'value_mora_land': self.value_mora_land


                })

                record.days_expired_land = None
                #record.invoice_line_ids += self.env['account.move.line'].new()




        return res



    def action_post(self):
        res = super().action_post()
        self.get_narration()
        return res

    @api.depends('narration_text','bank_origin_ids','bank_origin_ids.bank_id',
                 'bank_origin_ids.operation_number','bank_origin_ids.date')
    def get_narration(self):
        for record in self:
            text = record.narration_text or ''

            if record.bank_origin_ids:
                salto = '\n' if len(record.bank_origin_ids) > 1 else ''
                text += f'\n DATOS DE DEPOSITO: '
                for bank in record.bank_origin_ids:
                    operation_number = '- ' +bank.operation_number if bank.operation_number else ''
                    bank_date = f' - {str(bank.date) }' if bank.date else ''
                    text += f'''{salto}  {bank.bank_id.name} {operation_number} {bank_date}'''

            record.narration_str = text


    def _get_document_values_generar_odoofact(self, ose_supplier):
        commercial = self.commercial_partner_id
        commercial_doc_type = commercial.l10n_latam_identification_type_id
        currency = CURRENCY.get(self.currency_id.name, False)
        return {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": self.l10n_latam_document_type_id.type_of,
            "serie": str(self.sequence_prefix)[0:4],
            "numero": self.sequence_number,
            "sunat_transaction": int(self.l10n_pe_edi_odoofact_operation_type),
            "cliente_tipo_de_documento": commercial_doc_type.l10n_pe_vat_code,
            "cliente_numero_de_documento": self.commercial_partner_id.vat,
            "cliente_denominacion": self.commercial_partner_id.name,
            "cliente_direccion": self._get_partner_address_odoofact(self.partner_id),
            "cliente_email": self.partner_id.email and self.partner_id.email or "",
            "fecha_de_emision": self.invoice_date.strftime("%d-%m-%Y"),
            "fecha_de_vencimiento": self.invoice_date_due
            and self.invoice_date_due.strftime("%d-%m-%Y")
            or "",
            "moneda": currency,
            "tipo_de_cambio": self.l10n_pe_edi_exchange_rate,
            "porcentaje_de_igv": self.l10n_pe_edi_igv_percent,
            "descuento_global": self.l10n_pe_edi_global_discount,
            "total_descuento": self.l10n_pe_edi_amount_discount,
            "total_anticipo": self.l10n_pe_edi_amount_advance,
            "total_gravada": self.l10n_pe_edi_amount_base,
            "total_inafecta": self.l10n_pe_edi_amount_unaffected,
            "total_exonerada": self.l10n_pe_edi_amount_exonerated,
            "total_igv": self.l10n_pe_edi_amount_igv,
            "total_gratuita": self.l10n_pe_edi_amount_free,
            "total_otros_cargos": 0.0,  # ---------
            "total_isc": 0.0,  # ---------
            "total": self.amount_total,
            "retencion_tipo": self.l10n_pe_edi_retention_type_id
            and int(self.l10n_pe_edi_retention_type_id.code)
            or "",
            "retencion_base_imponible": self.l10n_pe_edi_retention_type_id
            and abs(self.amount_total)
            or "",
            "total_retencion": self.l10n_pe_edi_retention_type_id
            and abs(self.l10n_pe_edi_total_retention)
            or "",
            "total_impuestos_bolsas": self.l10n_pe_edi_amount_icbper,
            "observaciones": self.narration_str or "",
            "documento_que_se_modifica_tipo": self.l10n_pe_edi_origin_move_id
            and (self.l10n_pe_edi_origin_move_id.name[0] == "F" and 1 or 2)
            or "",
            "documento_que_se_modifica_serie": self.l10n_pe_edi_origin_move_id
            and str(self.l10n_pe_edi_origin_move_id.sequence_prefix)[0:4]
            or "",
            "documento_que_se_modifica_numero": self.l10n_pe_edi_origin_move_id
            and self.l10n_pe_edi_origin_move_id.sequence_number
            or "",
            "tipo_de_nota_de_credito": self.l10n_pe_edi_reversal_type_id
            and int(self.l10n_pe_edi_reversal_type_id.code_of)
            or "",
            "tipo_de_nota_de_debito": self.l10n_pe_edi_debit_type_id
            and int(self.l10n_pe_edi_debit_type_id.code_of)
            or "",
            "enviar_automaticamente_a_la_sunat": "",  # ---------
            "enviar_automaticamente_al_cliente": self.l10n_pe_edi_shop_id.send_email
            and "true"
            or "false",
            "codigo_unico": "%s|%s|%s-%s"
            % (
                "odoo",
                self.company_id.partner_id.vat,
                str(self.sequence_prefix)[0:4],
                str(self.sequence_number),
            ),
            "condiciones_de_pago": self.invoice_payment_term_id
            and self.invoice_payment_term_id.name
            or "",
            "medio_de_pago": self.l10n_pe_edi_is_sale_credit
            and "venta_al_credito"
            or "contado",
            "orden_compra_servicio": self.l10n_pe_edi_service_order or "",
            "detraccion": self.l10n_pe_edi_detraction_type_id and "true" or "false",
            "detraccion_tipo": self.l10n_pe_edi_detraction_type_id
            and int(self.l10n_pe_edi_detraction_type_id.code_of)
            or "",
            "detraccion_total": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_total_detraction_signed
            or "",
            "detraccion_porcentaje": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_detraction_type_id.rate
            or "",
            "medio_de_pago_detraccion": self.l10n_pe_edi_detraction_type_id
            and self.l10n_pe_edi_detraction_payment_type_id
            and int(self.l10n_pe_edi_detraction_payment_type_id.code_of)
            or "",
            "generado_por_contingencia": self.journal_id.l10n_pe_edi_contingency
            and "true"
            or "false",
            "items": getattr(self, "_get_lines_values_generar_%s" % (ose_supplier))(),
            "guias": getattr(self, "_get_guides_values_generar_%s" % (ose_supplier))(),
            "venta_al_credito": getattr(
                self, "_get_dues_values_generar_%s" % (ose_supplier)
            )(),
        }


class BankOrigin(models.Model):
    _name = 'bank.origin'
    bank_id = fields.Many2one('res.bank',string="Banco",required=True)
    operation_number = fields.Char(string="N° Operacion")
    date = fields.Date(string="Fecha")
    move_id = fields.Many2one('account.move')