from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty


from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    groupby,
    index_exists,
    is_html_empty,
)

CURRENCY = {
    "PEN": 1,
    "USD": 2,
    "EUR": 3,
    "GBP": 4,
}
from datetime import datetime, timedelta

class AccountMove(models.Model):
    _inherit = 'account.move'
    narration_text = fields.Text(copy=False)

    narration_str = fields.Text(compute="get_narration",store=True,copy=False)
    bank_origin_ids = fields.One2many('bank.origin','move_id',string="Cuentas Bancarias",copy=False)
    is_separation_land = fields.Boolean(string="Es una Separación Terreno",copy=False)
    is_initial_land = fields.Boolean(string="Es Inicial Terreno",compute='get_is_initial_land',copy=False)
    is_independence = fields.Boolean(string="Es Idependizacion", compute='get_is_initial_land', store=True)
    days_expired_land = fields.Integer(copy=False)
    value_mora_land = fields.Float(string="Precio Mora", default=10,copy=False)

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
    mz_land_separation_id  = fields.Many2one('product.attribute.value',domain=[('attribute_id.type_land','=','mz')],string="MZ")
    lot_land_separation_id = fields.Many2one('product.attribute.value',domain=[('attribute_id.type_land','=','lot')],string="Lote")
    sector_land_separation_id = fields.Many2one('product.attribute.value',domain=[('attribute_id.type_land','=','stage')],string="Etapa")
    sale_order_count_store = fields.Integer(related='sale_order_count',store=True)
    days_count_expired_separation = fields.Integer(compute='get_days_count_expired_separation',string="Dias Expirados")
    amount_due_land = fields.Float(compute='get_is_initial_land')
    qty_due_land = fields.Float(compute='get_is_initial_land')
    amount_mora_land = fields.Float(compute='get_is_initial_land')
    report_lot_land_line_id = fields.Many2one('report.lot.land.line',  store=True,string="LOte")
    stage_separation_land = fields.Selection([
        ('active','Activo'),
        ('down','Caido'),
        ('initial','Inicial')
    ],string='Estado Separación')

    proveedores_land   = fields.Char(compute="get_proveedores_land",store=True,string="Proveedor",copy=False)
    mz_lot             = fields.Char(string="MZ-LT", compute="get_proveedores_land",store=True,copy=False)
    description_land   = fields.Char(string="Descripcion", compute="get_proveedores_land")
    nro_internal_land  = fields.Char(string="Expediente", compute="get_proveedores_land")

    @api.depends('invoice_line_ids','invoice_line_ids.sale_line_ids')
    def get_proveedores_land(self):
        for record in self:
            proveedor = []
            mz_lot = None
            description_land = ''
            nro_internal_land = ''

            for line in record.invoice_line_ids:
                if line.sale_line_ids:
                    for sale_line in line.sale_line_ids:
                        order = sale_line.order_id
                        mz_lot = order.mz_lot
                        nro_internal_land = order.nro_internal_land
                        if order.seller_land_id:
                            if order.seller_land_id.name not in proveedor:
                                proveedor.append(order.seller_land_id.name)
                #if line.product_id.payment_land_dues:

                description_land += line.name or  ''

            record.proveedores_land = ",".join(proveedor) if proveedor else None
            record.mz_lot = mz_lot
            record.description_land = description_land
            record.nro_internal_land = nro_internal_land



    vat = fields.Char(related='partner_id.vat',string="RUC/DNI")
    identification_type = fields.Char(related='partner_id.l10n_latam_identification_type_id.name',string="Doc")
    l10n_pe_vat_code    = fields.Char(related='partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code',string="Codigo Doc")
    banks_str           = fields.Text(compute="get_banks_str",string='Banco-Operación')
    bank_name           = fields.Text(compute="get_banks_str",string='Banco')
    bank_operation = fields.Text(compute="get_banks_str", string='Operación')
    bank_date = fields.Date(compute="get_banks_str", string='Fecha Operación')
    def get_banks_str(self):
        for record in self:
            bank_name = []
            bank_operation = []
            bank_date = []
            texts = ''
            c = 0
            for bank in record.bank_origin_ids:
                bank_name.append(bank.bank_id.name)
                bank_operation.append(str(bank.operation_number))
                bank_date.append(str(bank.date))
                if c == 0 :
                    texts += f''' {bank.bank_id.name} - {bank.operation_number} - {bank.date} '''
                else:
                    texts += f'''\n {bank.bank_id.name} - {bank.operation_number} - {bank.date} '''
                c += 1

            record.bank_name = '\n'.join(bank_name) if bank_name else ''
            record.bank_operation = '\n'.join(bank_operation) if bank_operation else ''
            record.bank_date = '\n'.join(bank_date) if bank_date else ''


            record.banks_str = texts



    def write(self,vals):
        res = super().write(vals)
        if 'payment_reference' in vals:
            self.validate_date_nubefact()
            self.get_narration_dx()

        self.update_order_jz()

        return res

    #este use para actulizar la fecha si por alguna razon es diferente a la que se publico en nubefact
    #@api.onchange('payment_reference')
    def validate_date_nubefact(self):

        self.get_narration_dx()

        '''
        
        for record in self:
            if  record.l10n_pe_edi_request_id.document_date  :
                if record.l10n_pe_edi_request_id.document_date != record.invoice_date:
                    record.invoice_date =  record.l10n_pe_edi_request_id.document_date

        '''


    def update_all_moves(self):
        moves = self.env['account.move'].search([])
        moves[11000:12000].get_proveedores_land()


    @api.onchange('mz_land_separation_id', 'lot_land_separation_id')
    def get_report_lot_land_line_id(self, product_tmp=None):
        for record in self:


            line = None
            # raise ValueError(product_tmp)

            if record.mz_land_separation_id and record.lot_land_separation_id:
                line = self.env['report.lot.land.line'].search([
                    ('mz_value_id.name', '=', record.mz_land_separation_id.name),
                    ('name', '=', str(int(record.lot_land_separation_id.name))),
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
            is_independence = False

            for line in record.invoice_line_ids:
                if line.product_id.is_advanced_land:
                    is_initial = True

                if line.product_id.is_independence:
                    is_independence = True

                if line.product_id.is_mora_land:
                    amount_mora += line.price_total
                else:
                    qty_due = line.quantity
                    amount_due += line.price_total
            record.qty_due_land = qty_due
            record.is_initial_land = is_initial
            record.amount_due_land = amount_due
            record.amount_mora_land = amount_mora
            record.is_independence = is_independence

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

        #note = f' SEPARADO PARA {self.mz_land_separation_id.name}-{ self.lot_land_separation_id.name} , {self.sector_land_separation_id.name} '

        return {
            "name": f"Cotizacion",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order",
            "target": "current",
            "context": {
                'default_move_separation_land_id': self.id  ,
                'default_partner_id': self.partner_id.id ,
                #'default_note': note
            }

        }


    def update_order_jz(self):
        for record   in self:
            orders = []
            for line in record.invoice_line_ids:
                if line.sale_line_ids:
                    for sale_line in line.sale_line_ids:
                        if not sale_line.order_id in orders:
                            orders.append(sale_line.order_id)
            for order in orders:
                order.update_schedule()
                #order._get_stage_payment_land()
                #order.get_last_payment_date_land()

                order.update_credit_saldo()



    @api.model
    def create(self,vals):



        res = super(AccountMove, self).create(vals)


        for record in res:
            self.env['sale.order'].verifi_mz_lot(mz=record.mz_land_separation_id.name, lt=record.lot_land_separation_id.name,object= record)




            for line in record.invoice_line_ids:
                if line.product_id.is_advanced_land:
                    if line.product_id.description_sale:
                        record.narration_text = line.product_id.description_sale
                if line.product_id.is_separation_land:
                    record.is_separation_land = True
                    record.stage_separation_land = 'initial'

                    #colocar la manza y lote







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


        #verificar mz y lote
        res.update_order_jz()






        return res

    def action_post(self):

        for line in self.invoice_line_ids:
            if line.order_advance_land and not line.sale_line_ids :

                order_line = self.env['sale.order.line'].create({
                    'product_id': line.product_id.id ,
                    'name': line.name ,
                    'order_id': line.order_advance_land.id ,
                    'price_unit': 0 , #line.price_unit
                    'tax_id': [(6,0,line.tax_ids.ids)] ,
                    'customer_lead': 1 ,
                    'product_uom_qty': 1 ,
                    'number_advance_land': line.number_advance_land
                })

                order_line.invoice_lines = [(6,0,[line.id])]

                #line.sale_line_ids = [(6,0,[order_line.id])]



        res = super().action_post()
        self.get_narration_dx()
        self.update_order_jz()
        return res

    def button_cancel(self):

        res = super().button_cancel()
        self.update_order_jz()
        return res

    @api.depends('narration_text','bank_origin_ids','bank_origin_ids.bank_id',
                 'bank_origin_ids.operation_number','bank_origin_ids.date')
    def get_narration_dx(self):
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
        has_advance_payment = self.l10n_pe_edi_odoofact_operation_type
        apply_detraction = self.l10n_pe_edi_detraction_type_id and True or False
        values = {
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
            "detraccion": "true" if has_advance_payment == "4" and apply_detraction == True else (self.l10n_pe_edi_detraction_type_id and "true" or "false"),
            "generado_por_contingencia": self.journal_id.l10n_pe_edi_contingency
            and "true"
            or "false",
            "items": getattr(self, "_get_lines_values_generar_%s" % (ose_supplier))(),
            "guias": getattr(self, "_get_guides_values_generar_%s" % (ose_supplier))(),
            "venta_al_credito": getattr(
                self, "_get_dues_values_generar_%s" % (ose_supplier)
            )(),
        }
        if not (has_advance_payment == "4" and apply_detraction == True):
            values.update({
                "detraccion_tipo": self.l10n_pe_edi_detraction_type_id and int(self.l10n_pe_edi_detraction_type_id.code_of) or "",
                "detraccion_total": self.l10n_pe_edi_detraction_type_id and self.l10n_pe_edi_total_detraction_signed or "",
                "detraccion_porcentaje": self.l10n_pe_edi_detraction_type_id and self.l10n_pe_edi_detraction_type_id.rate or "",
                "medio_de_pago_detraccion": self.l10n_pe_edi_detraction_type_id and self.l10n_pe_edi_detraction_payment_type_id and int(self.l10n_pe_edi_detraction_payment_type_id.code_of) or "",
            })
        return values


    #override
    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.ref:
                        #reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                        reconciliation_ref = counterpart_line.move_id.ref
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False

                    reconciled_vals.append({
                        'name': counterpart_line.name,
                        'journal_name': counterpart_line.journal_id.name,
                        'company_name': counterpart_line.journal_id.company_id.name if counterpart_line.journal_id.company_id != move.company_id else None,
                        'amount': reconciled_partial['amount'],
                        'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else
                        reconciled_partial['currency'].id,
                        'date': counterpart_line.date,
                        'partial_id': reconciled_partial['partial_id'],
                        'account_payment_id': counterpart_line.payment_id.id,
                        'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                        'move_id': counterpart_line.move_id.id,
                        'ref': reconciliation_ref,
                        # these are necessary for the views to change depending on the values
                        'is_exchange': reconciled_partial['is_exchange'],
                        'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance),
                                                              currency_obj=counterpart_line.company_id.currency_id),
                        'amount_foreign_currency': foreign_currency and formatLang(self.env,
                                                                                   abs(counterpart_line.amount_currency),
                                                                                   currency_obj=foreign_currency)
                    })
                payments_widget_vals['content'] = reconciled_vals

            if payments_widget_vals['content']:
                move.invoice_payments_widget = payments_widget_vals
            else:
                move.invoice_payments_widget = False

    def add_adelanto_land(self):
        return {
            "name": f"AGREGAR ADELANTO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref('land.form_account_move_line').id,
            "res_model": "account.move.line",
            #"res_id": self.id,
            "target": "new",
            "context": {
                'default_move_id': self.id ,
                'default_move_type': self.move_type ,
                'default_journal_id': self.journal_id.id ,
                'default_partner_id': self.commercial_partner_id.id,
                'default_currency_id': self.currency_id.id ,
                'default_display_type': 'product' ,
                #'quick_encoding_vals': quick_encoding_vals,
            }

        }

class BankOrigin(models.Model):
    _name = 'bank.origin'
    bank_id = fields.Many2one('res.bank',string="Banco",required=True)
    operation_number = fields.Char(string="N° Operacion")
    date = fields.Date(string="Fecha")
    move_id = fields.Many2one('account.move')
