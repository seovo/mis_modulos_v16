from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_id = fields.Many2one(
        comodel_name='res.users',
        domain=lambda self: "[('company_ids', '=', company_id)]"
    )
    #############

    nro_internal_land =  fields.Char(string="Expediente",copy=False)
    mz_lot            =  fields.Char(string="MZ - LOTE",copy=False)
    sector            =  fields.Char(string="Etapa",copy=False)
    sectorr           =  fields.Char("Sector",copy=False)
    stage_land           = fields.Selection([
        ('signed',_('Firmado'))  ,
        ('preaviso',_('Carta Preaviso')),
        ('cancel',_('Resuelto')),
        ('regularizado','Regularizado'),
    ],string="Estado Terreno",copy=False)
    dues_land            = fields.Float(string="Cuotas",copy=False)
    value_due_land       = fields.Float(string="Precio Cuota",copy=False,compute='get_amount_prices_land',digits=(12, 3))
    crono_land           = fields.Char(string="Crono",copy=False)
    days_tolerance_land  = fields.Integer(string="Dias de Gracia",default=3,copy=False)
    value_mora_land = fields.Float(string="Precio Mora",default=10,copy=False)
    percentage_refund_land = fields.Float(string="Porcentaje Devolucion",copy=False)

    date_sign_land = fields.Date(string="Fecha Firma del Contrato",copy=False)
    date_first_due_land = fields.Date(string="Fecha Primera Cuota",copy=False)
    repeat_mz_lot  = fields.Boolean(string='Repetir MZ - LT',copy=False)


    modality_land = fields.Selection([
        ('single',_('Soltero')) ,
        ('low_customer',_('Baja cliente')) ,
        ('married',_('Casado')) ,
        ('divorcee',_('Divorciado')) ,
        ('confirmer',_('Confirmador')) ,
        ('widow',_('Viudo')) ,
        ('transfer',_('Transferencia')) ,
        ('legal','Persona Juridica'),
        ('attorney','Representante Apoderado')
    ],string="Modalidad",copy=False)

    obs_modality_land = fields.Text(string="Observaciones",copy=False)
    obs_resolution = fields.Text(string="Observacion Resolucion",copy=False)


    price_total_land = fields.Float(string="Valor del Terreno",compute="get_amount_prices_land",store=True,copy=False)
    price_initial_land = fields.Float(string="Inicial del Terreno",compute="get_amount_prices_land",store=True,copy=False)
    price_credit_land = fields.Float(string="Credito del Terreno",compute="get_amount_prices_land",store=True,copy=False)
    price_independence_land = fields.Float(string="Independización Terreno",compute="get_amount_prices_land",store=True,copy=False)

    @api.onchange('order_line', 'order_line.price_unit','order_line.product_uom_qty','repeat_mz_lot')
    @api.depends('order_line', 'order_line.price_unit','order_line.product_uom_qty','repeat_mz_lot')
    def get_amount_prices_land(self):
        for record in self:

            price_inicial = 0
            price_credit = 0
            price_iden = 0
            dues_land = 0
            value_due = 0
            for line in record.order_line:
                if line.product_id.is_advanced_land and not line.is_due_land:
                    price_inicial += line.price_total
                if ( line.product_id.payment_land_dues or line.is_due_land ) and not line.product_id.is_independence:
                    price_credit += line.price_total
                    dues_land += line.product_uom_qty
                    value_due = line.price_unit

                if line.product_id.is_independence:
                    price_iden += line.price_total



            record.price_initial_land = price_inicial
            record.price_credit_land =  price_credit
            record.price_total_land = price_inicial + price_credit
            record.price_independence_land = price_iden
            record.dues_land = dues_land

            record.value_due_land = value_due

    note = fields.Text()
    seller_land_id = fields.Many2one('seller.land',string="Proveedor Terreno",copy=False)


    #esto es para importar
    journal_import_id = fields.Integer(copy=False)
    price_unit_import = fields.Float(copy=False)
    invoice_payment_import_id = fields.Integer(copy=False)
    invoice_date_import =  fields.Date(copy=False)
    #journal_id = fields.Many2one('account.journal',string="Diario",copy=False)
    move_separation_land_id = fields.Many2one('account.move',string='Factura Separación')

    stage_payment_lan = fields.Selection([
        ('separation','Separado'),
        ('initial','Inicial Incompletada'),
        ('dues','Cuotas Pendientes'),
        ('payment', 'Pagando Cuotas'),
        ('completed','Cuotas Completada')
    ],compute='_get_stage_payment_land',store=True,string='Etapa Pago  Terreno')

    last_payment_date_land = fields.Date(string="Ultima Fecha de Pago",compute="get_last_payment_date_land",store=True)
    next_payment_date_land = fields.Date(string="Proxima Fecha de Pago", compute="get_last_payment_date_land",store=True)
    days_expired_land = fields.Integer(string="Dias Vencidos", compute="get_last_payment_date_land")

    mora_acumulada    = fields.Float(string="Mora Acumulada", compute="get_last_payment_date_land")
    mounth_expired_land = fields.Integer(string="Meses Vencidos", compute="get_last_payment_date_land",store=True)
    amount_payment_month_land = fields.Float(string="Total Mensualidad", compute="get_last_payment_date_land", store=True)
    amount_total_payment_month_land = fields.Float(string="Total a Pagar", compute="get_last_payment_date_land",
                                               store=True)


    type_periodo_invoiced  = fields.Selection([('half_month','Quincenal'),('end_month','Fin de Mes')],
                                              string="Periodo de Facturación")
    schedule_land_ids = fields.One2many('schedule.dues.land','order_id')
    mz_land = fields.Char(store=True,string="Manzana Terreno")
    lot_land = fields.Char(store=True,string="Lote Terreno")
    sector_land = fields.Char(store=True, string="Etapa Terreno")
    m2_land = fields.Char(string="AREA (m2)")
    total_payment_land = fields.Float(string='Total Pagado Cuotas')
    saldo_payment_land = fields.Float(string='Saldo Cuotas')
    qty_dues_payment   = fields.Integer(compute='get_qty_dues_payment',string="Cuotas Pagadas")
    commision_lan     = fields.Float(string='Commision Terreno')
    commision_line_ids       = fields.One2many('commission.land.line','sale_id')

    state_lawyer_land  = fields.Selection([('draft','Pendiente'),('sent','Enviado')],default='draft',string='Envio Reporte Abogado')
    sale_line_payment_id = fields.Many2one('sale.order.line', string="Especificar Pago")

    comision_payment = fields.Float(string="Comision Pagada",compute='get_comision_payment')
    comision_payment_real = fields.Float(string="Comision Pagada (Con Descuentos)", compute='get_comision_payment')
    diff_payment_comision =  fields.Float(string="Diferencia Comision", compute='get_comision_payment',store=True)

    ########
    product_tmp_lot_id  = fields.Many2one('product.template',string="Proyecto",
                                       domain="[('company_id', 'in', (False, company_id)),"
                                              "('payment_land_dues','=',True),('sale_ok','=',True)]"
                                       )
    report_lot_land_line_id = fields.Many2one('report.lot.land.line',
                                              string="Lote",
                                              domain="[('product_tmp_id', '=', product_tmp_lot_id)]")
    area_lot_related = fields.Float(related='report_lot_land_line_id.area',readonly=False,string="Area")
    zona_lot_related = fields.Many2one('land.zona',related='report_lot_land_line_id.zona',readonly=False,string="Zona")
    ettapa_lot_related = fields.Char(related='report_lot_land_line_id.ettapa', readonly=False,
                                       string="Etapa")
    price_lot_related = fields.Float(string='Precio',related='report_lot_land_line_id.price')
    ###########

    inicial_lot_set = fields.Float(string="Inicial")
    price_m2 = fields.Float(string='Precio M2',digits=(12, 3))

    paid_land_1 = fields.Float(compute='get_amounts_paid_land',string='Ene')
    paid_land_2 = fields.Float(compute='get_amounts_paid_land', string='Feb')
    paid_land_3 = fields.Float(compute='get_amounts_paid_land', string='Mar')
    paid_land_4 = fields.Float(compute='get_amounts_paid_land', string='Abr')
    paid_land_5 = fields.Float(compute='get_amounts_paid_land', string='May')
    paid_land_6 = fields.Float(compute='get_amounts_paid_land', string='Jun')
    paid_land_7 = fields.Float(compute='get_amounts_paid_land', string='Jul')
    paid_land_8 = fields.Float(compute='get_amounts_paid_land', string='Agos')
    paid_land_9 = fields.Float(compute='get_amounts_paid_land', string='Sep')
    paid_land_10 = fields.Float(compute='get_amounts_paid_land', string='Oct')
    paid_land_11 = fields.Float(compute='get_amounts_paid_land', string='Nov')
    paid_land_12 = fields.Float(compute='get_amounts_paid_land', string='Dic')
    credit_year_now = fields.Float(compute='get_amounts_paid_land', string='Credito Anual')
    payment_year_now = fields.Float(compute='get_amounts_paid_land', string='Aportado Anual')
    saldo_year_now = fields.Float(compute='get_amounts_paid_land', string='Saldo Anual')

    @api.depends('schedule_land_ids')
    def get_amounts_paid_land(self):
        year = fields.Datetime.now().year
        for record in self:
            record.paid_land_1 = None
            record.paid_land_2 = None
            record.paid_land_3 = None
            record.paid_land_4 = None
            record.paid_land_5 = None
            record.paid_land_6 = None
            record.paid_land_7 = None
            record.paid_land_8 = None
            record.paid_land_9 = None
            record.paid_land_10 = None
            record.paid_land_11 = None
            record.paid_land_12 = None

            credit_year_now = 0
            payment_year_now = 0
            saldo_year_now = 0

            for sche in record.schedule_land_ids:
                datex = sche.date

                if datex and datex.year == year:
                    if datex.month == 1 :
                        record.paid_land_1 = sche.amount_due_land

                    if sche.amount_due_land > 0 :
                        record[f'paid_land_{datex.month}'] = sche.amount_due_land
                        payment_year_now += sche.amount_due_land
                    else:
                        record[f'paid_land_{datex.month}'] = -1 * sche.amount
                        saldo_year_now += sche.amount

                    credit_year_now += sche.amount

            record.credit_year_now = credit_year_now
            record.payment_year_now = payment_year_now
            record.saldo_year_now = saldo_year_now




    @api.onchange('report_lot_land_line_id')
    def change_report_lot_land(self):
        for record in self:
            if record.report_lot_land_line_id and not record.order_line:
                record.inicial_lot_set = record.report_lot_land_line_id.product_tmp_id.optional_product_ids[0].list_price
                record.price_m2 = record.report_lot_land_line_id.zona.value
                record.seller_land_id = record.report_lot_land_line_id.seller_land_id.id



    @api.onchange('seller_land_id')
    def changer_seller_land_id(self):
        for record in self:
            if not record.report_lot_land_line_id:
                continue
            record.report_lot_land_line_id.seller_land_id = record.seller_land_id.id if record.seller_land_id else None

    @api.onchange('zona_lot_related','area_lot_related')
    def change_zona_area(self):
        for record in self:

            if record.order_line:
                continue

            if record.area_lot_related and record.zona_lot_related:
                record.price_lot_related = record.area_lot_related * record.zona_lot_related.value

            if record.zona_lot_related:
                record.price_m2 = record.zona_lot_related.value

            if record.area_lot_related:
                record.m2_land = record.area_lot_related



    def open_product_land(self):
        return {
            "name": f"AGREGAR TERRENO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref('land.add_terreno_sale').id,
            "res_model": "sale.order",
            "res_id": self.id,
            "target": "new",
            #"context": {
            #    'default_order_id': self.id
            #}

        }


    @api.depends('commision_line_ids','commision_line_ids.commission_land_id.state')
    def get_comision_payment(self):
        for record in self:
            payment = 0
            payment_real = 0
            for line in record.commision_line_ids:
                if line.commission_land_id.state == 'done' :
                    payment += line.amount
                    payment_real += line.subtotal

            record.comision_payment = payment
            record.comision_payment_real = payment_real
            record.diff_payment_comision = payment - payment_real


    @api.onchange('nro_internal_land')
    def change_nro_internal_land(self):
        for record in self:
            if record.nro_internal_land and not  record.stage_land:
                record.stage_land = 'signed'


    def update_dates_land(self):
        for invc in self.invoice_ids:
            if invc.amount_total == self.price_initial_land:
                invc.invoice_date = self.date_sign_land

            if invc.state == 'draft':
                invc.action_post()
            #    exist_confirm = True

        if self.price_total_land and self.price_total_land != 0 and len(
                self.invoice_ids) > 1 and self.date_first_due_land:
            invoices = self.env['account.move'].search([
                ('id', 'in', self.invoice_ids.ids),
            ], order='invoice_date asc')
            date_init = self.date_first_due_land
            is_end_month = False
            if date_init.day > 25 and date_init.day <= 31:
                is_end_month = True

            c = 0
            for invoice in invoices:

                if c > 0:
                    if is_end_month:
                        cx = c - 1
                        if cx > 0 :
                            date_initx = date_init + relativedelta(months=cx)
                        else:
                            date_initx = date_init




                        last_date = datetime(date_initx.year if date_initx.month != 12 else date_initx.year + 1,
                                             date_initx.month + 1 if date_initx.month != 12 else 1, 1) - timedelta(
                            days=1)

                        if last_date.day != date_init.day:
                            date_initx = last_date

                    else:
                        cx = c - 1
                        if cx > 0:
                            date_initx = date_init + relativedelta(months=cx)
                        else:
                            date_initx = date_init

                    invoice.invoice_date = date_initx
                c += 1


    @api.onchange('user_id')
    def  change_team_comission(self):
        for record in self:
            teams = self.env['crm.team'].search([])
            for team in teams:
                if record.user_id in team.member_ids:
                    record.commision_lan = team.commission_land

    #@api.onchange('mz_land','lot_land','state','mz_lot','note')
    def get_report_lot_land_line_id(self):

        for record in self:

            mz_land =  None
            lot_land =  None
            product_tmp = None
            '''
            for line in  record.order_line:
                for at in line.product_id.product_template_attribute_value_ids:
                    #product_tmp = line.product_id.product_tmpl_id
                    typex = at.attribute_id.type_land
                    if typex == 'mz':
                        mz_land = at.name
                    if typex == 'lot':
                        lot_land = at.name
            '''

            #raise ValueError([mz_land,lot_land])


            if not mz_land or not lot_land:
                for line in record.order_line:
                    if line.invoice_lines and (line.product_id.payment_land_dues  or line.product_id.is_independence):
                        #product_tmp = line.product_id.product_tmpl_id
                        if len(line.invoice_lines) >  1 :
                            invoices = line.invoice_lines[0]
                            import re


                            texto = invoices.name
                            texto = texto.replace('-2025','')
                            texto = texto.replace('MZ','')
                            texto = texto.replace('LT', '')
                            texto = texto.replace(':', '')
                            texto = texto.replace(' ', '')

                            #coincidencia = re.search(r'\b[A-Z]\d-\d{2}\b', texto)
                            #coincidencia = re.search(r'\b[A-Z]-\d{2}\b', texto)
                            #coincidencia = re.search(r'\b[A-Z]\d{1,2}-\d{1,2}\b', texto)
                            coincidencia = re.search(r',([^,]+),', texto)

                            #raise ValueError([texto , coincidencia, mz_land, lot_land])


                            if coincidencia:
                                codigo = coincidencia.group()
                                codigo = codigo.replace(',','')
                                codigo = codigo.split('-')

                                try:
                                    mz_land = codigo[0].replace(' ', '')
                                    lot_land = codigo[1].replace(' ', '')
                                except:
                                    continue
                                #raise ValueError([texto, coincidencia, mz_land, lot_land])

                            else:
                                continue
                                #raise ValueError(texto)
                            #raise ValueError(invoices.name)





            line = None

            #raise ValueError(product_tmp)

            if mz_land and lot_land :

                dm = [('manzana', '=', mz_land),
                      ('name', '=', str(int(lot_land))), ('product_tmp_id', '=', 3)]
                line = self.env['report.lot.land.line'].search(dm)



                '''    
                try:
                    dm = [('manzana', '=', mz_land),
                          ('name', '=', str(int(lot_land))), ('product_tmp_id', '=', 3)]
                    line = self.env['report.lot.land.line'].search(dm)
                except:

                    continue
                '''
                if not line:
                    raise ValueError([line, dm,record])
                    continue
                    #raise ValueError(dm)


                if len(line) > 1:
                    continue


            if line:
                record.report_lot_land_line_id = line





    def show_dues_land(self):
        self.update_schedule()
        return {
            "name": f"PAGOS",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref('land.view_order_form_due').id ,
            "res_model": "sale.order",
            "res_id": self.id,
            "target": "new",

        }

    def get_qty_dues_payment(self):

        for record in self:
            cantidad_facturada = 0
            for line in record.order_line:
                if line.product_id.payment_land_dues:

                    for line_inv in line.invoice_lines:

                        if line_inv.move_id.state == 'cancel':
                            continue

                        if line_inv.move_id.l10n_pe_edi_reversal_type_id:
                            continue

                        if line_inv.move_id.payment_state ==  'reversed':
                            continue

                        if not line_inv.move_id.debit_origin_id:
                            cantidad_facturada += line_inv.quantity
                    #qty += line.qty_invoiced
            record.qty_dues_payment = cantidad_facturada

    @api.onchange('date_sign_land','type_periodo_invoiced')
    @api.depends('date_sign_land', 'type_periodo_invoiced')
    def change_date_first_due_date(self):
        for record in self:
            if record.date_sign_land and record.type_periodo_invoiced:
                date_next = record.date_sign_land +  relativedelta(months=1)
                if record.type_periodo_invoiced == 'half_month':
                    date_next = datetime(year=date_next.year,month=date_next.month,day=15,hour=10)
                    date_next = date_next.date()

                if record.type_periodo_invoiced == 'end_month':
                    date_next = datetime(year=date_next.year, month=date_next.month, day=1, hour=10) +  relativedelta(months=1)
                    date_next = date_next - timedelta(days=1)
                    date_next = date_next.date()

                record.date_first_due_land = date_next

    def show_lot_availables(self):
        product = self.env['product.template'].search([('payment_land_dues','=',True),('sale_ok','=',True)])
        product.update_lots_jz()

        return {
            "name": f"LOTES",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,tree",
            # "view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "report.lot.land.line",
            "res_id": product.id,
            "target": "current",
            "domain": [('product_tmp_id', '=', product.id)],
            "context": {
                'search_default_gr_mz_value_id': 1
            }

        }



    def update_all_seller_lot(self):
        for record in self:
            if record.id in [760 ,  804]  or record._origin.id in [760 ,  804] :
                continue
            if record.seller_land_id:
                if not  record.report_lot_land_line_id:
                    raise ValueError(record.name)
                record.report_lot_land_line_id = record.seller_land_id.id


    def update_all_info_land(self):
        record = self.env['sale.order'].search([])
        record.get_info_land()
        record.update_all_seller_lot()



    @api.onchange('order_line','sector','order_line.price_unit',
                  'order_line.product_uom_qty','note','report_lot_land_line_id','report_lot_land_line_id.zona',
                  'report_lot_land_line_id.manzana','report_lot_land_line_id.name','report_lot_land_line_id.area',
                  'report_lot_land_line_id.ettapa','report_lot_land_line_id.price_m2'
                  )
    def get_info_land(self):

        #self.get_report_lot_land_line_id()

        for record in self:


            mz = None
            lt = None
            stage = None
            m2 = None

            if record.partner_id:
                if record.report_lot_land_line_id:
                    mz = record.report_lot_land_line_id.manzana
                    lt = record.report_lot_land_line_id.name
                    m2 = record.report_lot_land_line_id.area
                    stage = record.report_lot_land_line_id.ettapa

                else:

                    if record.state == 'done':
                        for line in record.order_line:
                            if line.product_id.manzana and line.product_id.manzana != '':
                                mz = line.product_id.manzana

                            if line.product_id.lote and line.product_id.lote != '':
                                lt = line.product_id.lote

                            if line.product_id.sector_land and line.product_id.sector_land != '':
                                stage = line.product_id.sector_land

                            if line.product_id.m2_land and line.product_id.m2_land != '':
                                m2 = line.product_id.m2_land

                        if record.mz_lot and not mz and not lt:
                            mz_lot = record.mz_lot.split('-')
                            if len(mz_lot) == 2:
                                mz = str(mz_lot[0])
                                lt = str(mz_lot[1])


            record.mz_land = mz if mz != 'None' else None
            record.lot_land = lt if lt != 'None' else None
            record.mz_lot = f'''{mz}-{lt}'''

            if not stage and record.sector:
                stage = record.sector

            if stage:
                record.sector_land = stage

            if m2:
                record.m2_land = m2


    def update_credit_saldo(self):
        for record in self:
            total_payment = 0

            for line in record.order_line:
                if line.product_id.payment_land_dues:
                    for line_invoice in line.invoice_lines:
                        if line_invoice.move_id.l10n_pe_edi_reversal_type_id:
                            continue
                        if line_invoice.move_id.state != 'cancel' and line_invoice.move_id.payment_state != 'reversed':
                            total_payment += line_invoice.price_total

            record.total_payment_land = round(total_payment, 2)
            record.saldo_payment_land = round(record.price_credit_land - total_payment, 2)


    def publish_invoice(self):
        for record in self:
            for line in record.schedule_land_ids:
                if line.move_id:
                    if line.move_id.state == 'draft' and line.move_id.journal_id.id == 10:
                        line.move_id.action_post()


    def recreate_schedule(self):
        for record in self:
            record.schedule_land_ids.unlink()
        self.update_schedule()


    def update_schedule_all(self):
        orders = self.env['sale.order'].search([])
        orders.update_schedule()
        orders.update_credit_saldo()


    def invoice_lines_available_land(self):
        invoice_lines_dues = []
        invoice_lines_initial = []
        qty_invoiced = 0

        for line in self.order_line:

            for line_inv in line.invoice_lines:

                if line_inv.move_id.move_type in ['out_refund']:
                    continue


                if line_inv.move_id.payment_state == 'reversed' or line_inv.move_id.l10n_pe_edi_reversal_type_id:
                    continue

                if line_inv.move_id.debit_origin_id or line_inv.move_id.state == 'cancel':
                    continue


                #para cuotas
                if line.product_id.payment_land_dues and not line.product_id.is_independence:
                    qty_invoiced += line_inv.quantity
                    x = range(int(line_inv.quantity))

                    for n in x:
                        invoice_lines_dues.append(line_inv)

                #para iniciales
                if line.product_id.is_advanced_land or line.product_id.is_separation_land:
                    invoice_lines_initial.append(line_inv)



        if invoice_lines_dues:
            invoice_lines_dues.reverse()

        return qty_invoiced , invoice_lines_dues , invoice_lines_initial




    @api.depends('order_line', 'invoice_ids', 'invoice_ids.state','date_first_due_land','date_first_due_land')
    def update_schedule(self):
        for record in self:

            #si tiene fecha de inicio del cronograma

            if record.date_first_due_land:

                record.get_amount_prices_land()

                qty_dues = record.dues_land
                total_dues = record.price_credit_land
                #price_unit = record.value_due_land
                qty_invoiced , invoice_lines , invoice_lines_initial = record.invoice_lines_available_land()


                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('type_number_schedule','=',1),('order_id','=',record.id)
                ])

                if schedule_land_dues:
                    c = 0
                    for sche in schedule_land_dues:
                        dx = {
                            'number_due' : c + 1 ,
                            'date': None ,
                            'balan': 0 ,
                            #'amount': 0 ,
                            'is_paid' : False ,
                            'line_move_id': False ,
                            'invoice_date': False ,
                            'nro_internal_land': False ,
                            'type_number_schedule': 1
                        }
                        sche.write(dx)
                        c += 1

                else:
                    #crear cuotas
                    if qty_dues > 0:

                        for i in range(int(qty_dues)):
                            dx = {
                                'number_due' : i + 1 ,
                                'type_number_schedule': 1
                            }
                            record.schedule_land_ids += self.env['schedule.dues.land'].new(dx)


                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('type_number_schedule','=',1),('order_id','=',record.id)
                ])

                #crear las fechas previstas y balances
                datex = record.date_first_due_land
                i = 0
                for sche in schedule_land_dues:
                    sche.write({
                        'date': datex ,
                        'balan': total_dues - (i*record.value_due_land) ,
                    })

                    i += 1

                    #predecir la siguiente fecha futura

                    datex = datex +  relativedelta(months=1)

                    if datex.day > 24:
                        datex = datetime(year=datex.year, month=datex.month, day=1, hour=10) +  relativedelta(months=1)
                        datex = datex - timedelta(days=1)

                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('type_number_schedule','=',1),('order_id','=',record.id)
                ])

                #rellenar las facturas secuencialmente

                c = 0

                for inv_line in invoice_lines:
                    if inv_line.number_advance_land > 0 :
                        pass
                    else:
                        schedule_land_dues[c].write({
                            'is_paid': True ,
                            'line_move_id': inv_line.id
                        })






                #####lo antiguo
                continue



                if not schedule_land_dues :


                    if qty_dues > 0:
                        datex = record.date_first_due_land
                        for i in range(int(qty_dues)):
                            dx = {
                                'number_due' : i + 1 ,
                                'date': datex ,
                                'balan': total_dues - (i*price_unit) ,
                                'amount': price_unit ,
                                'is_paid' : True if (i + 1) <= qty_invoiced else False
                            }

                            #predecir la fecha futura

                            datex = datex +  relativedelta(months=1)

                            if datex.day > 24:
                                datex = datetime(year=datex.year, month=datex.month, day=1, hour=10) +  relativedelta(months=1)
                                datex = datex - timedelta(days=1)

                            try:
                                record.schedule_land_ids += self.env['schedule.dues.land'].new(dx)
                            except:
                                raise ValueError(dx)


                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('number_due','>',0),('order_id','=',record.id)
                ])

                if schedule_land_dues :

                    #invoices = self.env['account.move'].search([
                    #    ('id', 'in', record.invoice_ids.ids),
                    #    ('is_initial_land', '=', False),
                    #], order='invoice_date asc')

                    invoicesx = []
                    for linv in invoice_lines:
                        #if inv.is_initial_land:
                        #    continue

                        if linv.move_id.move_type in ['out_refund']:
                            continue

                        if linv.move_id.state == 'cancel':
                            continue

                        invoicesx.append(linv)

                        #for i in range(int(inv.qty_due_land)) :
                        #    invoicesx.append(inv)


                    i = 0
                    for linex in record.schedule_land_ids :
                        if linex.line_move_id.number_advance_land > 0 :
                            continue
                        linex.update({
                            'is_paid' : True if (i + 1) <= qty_invoiced else False ,

                        })
                        try:
                            linex.update({
                                'line_move_id': invoicesx[i].id
                            })
                            #total_payment += invoicesx[i].amount_due_land

                        except:
                            linex.update({
                                'line_move_id': False
                            })
                        i += 1


                #añadir adelantos
                factura_line_idsx = []

                for factura in record.invoice_ids:
                    for factura_line in factura.invoice_line_ids:
                        if not factura_line.sale_line_ids and factura_line.number_advance_land > 0:
                            factura_line_idsx.append(factura_line)

                if factura_line_idsx:
                    for factura_linex in factura_line_idsx:
                        df = [
                            '|', ('line_move_id', '=', factura_linex.id), ('line_move_id', '=', factura_linex._origin.id)
                        ]
                        #df = [('order_id','=',record.id),
                        #      ('number_due', '=', factura_linex.number_advance_land),
                        #
                        #      ]

                        df = [('order_id','=',record.id),('id_line_move_id', '=', factura_linex.id)]
                        exist_line = self.env['schedule.dues.land'].search(df)



                        dx = {
                            'number_due': factura_linex.number_advance_land,
                            'date': factura_linex.move_id.invoice_date,
                            'balan': 0,
                            'amount': factura_linex.price_unit,
                            'is_paid': True,
                            'line_move_id': factura_linex.id,
                            'order_id': record.id ,
                            'id_line_move_id': factura_linex.id
                        }

                        if not exist_line:
                            # raise ValueError([dx,exist_line])

                            record.schedule_land_ids += self.env['schedule.dues.land'].create(dx)
                        # else:
                        #    exist_line.write(dx)

                #Añadir iniciales:
                if invoice_lines_initial:
                    for inv_inicial in invoice_lines_initial:
                        df = [('order_id','=',record.id),('id_line_move_id', '=', inv_inicial.id)]
                        exist_line = self.env['schedule.dues.land'].search(df)

                        dx = {
                            'number_due': 0,
                            'date': inv_inicial.move_id.invoice_date,
                            'balan': 0,
                            'amount': inv_inicial.price_total,
                            'is_paid': True,
                            'line_move_id': inv_inicial.id,
                            'order_id': record.id ,
                            'id_line_move_id': inv_inicial.id
                        }

                        if not exist_line:
                            # raise ValueError([dx,exist_line])

                            record.schedule_land_ids += self.env['schedule.dues.land'].create(dx)





            record.update_credit_saldo()


        self.get_last_payment_date_land()
        self._get_stage_payment_land()
        self.get_amount_prices_land()


    @api.depends('invoice_ids','invoice_ids.state','date_first_due_land','date_first_due_land','type_periodo_invoiced')
    def get_last_payment_date_land(self):
        for record in self:
            date_now = fields.Datetime.now().date()
            date = None
            for invoice in record.invoice_ids:
                if invoice.state == 'posted':
                    if invoice.invoice_date and not invoice.debit_origin_id:
                        if not date:
                            date = invoice.invoice_date
                        else:
                            if invoice.invoice_date > date:
                                date = invoice.invoice_date

            #    date = record.date_first_due_land + relativedelta(months=1)
            record.last_payment_date_land = date



            date_next = None

            dues_payment = record.qty_dues_payment
            #for line in record.order_line:
            #    if line.product_id.payment_land_dues:
            #        dues_payment = line.qty_invoiced

            if  record.date_first_due_land:

                date_next = record.date_first_due_land

                if dues_payment > 0:
                    #dues_payment += 1
                    date_next = date_next +  relativedelta(months=dues_payment)


                if date_next.day <= 24 :
                    date_next = datetime(year=date_next.year,month=date_next.month,day=15,hour=10)
                    date_next = date_next.date()
                if date_next.day > 24:
                    date_next = datetime(year=date_next.year,month=date_next.month,day=1,hour=10) +  relativedelta(months=1)
                    date_next = date_next - timedelta( days=1)
                    date_next = date_next.date()

            record.next_payment_date_land = date_next

            diff_month = 0
            diff_days = 0

            if date_next:

                if date_now > date_next:
                    diff_days = (date_now - date_next).days

                #raise ValueError([diff_days,date_now,date_next,date_now - date_next])

            if date_next and record.qty_dues_payment > 0:
                #diff_month = ((date_now - date_next).days) / 30
                #hay que cambiar este calculo
                #diff_month += 1
                diff_month = self.env['schedule.dues.land'].search_count([
                    ('is_paid','!=',True),('order_id','=',record.id),('date','<=',date_now)])

            if date_next and record.qty_dues_payment == 0:
                diff_month = ((date_now - date_next).days) / 30



            record.mounth_expired_land = int(diff_month) if diff_month > 0 else 0
            record.amount_payment_month_land =  record.mounth_expired_land * record.value_due_land





            diff_days -= record.days_tolerance_land

            if diff_days < 0:
                diff_days = 0



            record.days_expired_land = diff_days

            record.mora_acumulada  = diff_days * record.value_mora_land

            record.amount_total_payment_month_land = record.amount_payment_month_land + record.mora_acumulada


    @api.depends('order_line','order_line.product_id','order_line.qty_invoiced',
                 'note','invoice_ids','invoice_ids.state','invoice_ids.invoice_date','repeat_mz_lot')
    def _get_stage_payment_land(self):
        #raise ValueError('okkk')
        for record in self:
            stage = None

            total_initial = 0
            total_initial_invoiced = 0
            total_separation_invoiced = 0
            total_anticipo_invoiced = 0

            total_dues = 0
            total_dues_invoiced = 0
            for line in record.order_line:

                if line.product_id.is_advanced_land and not line.is_due_land :
                    total_initial += line.product_uom_qty
                    total_initial_invoiced += line.qty_invoiced

                elif line.product_id.payment_land_dues or line.is_due_land:
                    total_dues += line.product_uom_qty
                    total_dues_invoiced +=  line.qty_invoiced

                elif line.product_id.is_separation_land:
                    total_separation_invoiced +=  line.qty_invoiced

                elif line.product_id.is_anticipo_land:
                    total_anticipo_invoiced += line.qty_invoiced



            if total_initial_invoiced < total_initial :

                if total_separation_invoiced > 0 :
                    stage = 'separation'

                if total_separation_invoiced and total_anticipo_invoiced > 0 :
                    stage = 'initial'

                if total_initial_invoiced > 0 :
                    stage = 'initial'


            if not stage and total_initial_invoiced > 0:
                if total_dues_invoiced < total_dues:
                    stage = 'dues'

                if total_dues_invoiced > 0:
                    stage = 'payment'

                #raise ValueError(stage)

                if total_dues_invoiced == total_dues:
                    stage = 'completed'

            record.stage_payment_lan = stage




    def _recalcule_price_land(self):
        for record in self:

            for line in record.order_line:
                if line.product_id and line.product_id.payment_land_dues:

                    line.change_product_uom_qty_land()



    def verifi_mz_lot(self,mz=None,lt=None,object=None):

        #esta funcion no funciona bien
        #reescribir

        return


        self2 = object or self



        mz_lot = None


        for record in self2:
            objectx = object if object else record

            if objectx._name == 'sale.order':

                #domain_order.append(('id', '!=', objectx.id))

                if objectx.repeat_mz_lot:
                    continue

            if objectx._name == 'sale.order.line':
                if objectx.order_id.repeat_mz_lot:
                    continue

            if objectx._name == 'account.move':
                if not objectx.is_separation_land:
                    continue

            #raise ValueError([mz,lt])
            #raise ValueError(record.mz_lot)
            if not mz and not lt:
                if objectx._name == 'sale.order':
                    if not record.mz_lot:
                        continue



            if mz and lt :
                mz_lot = f'{mz}-{lt}'
            else:
                if objectx._name == 'sale.order':
                    mz_lot = record.mz_lot

                    mz_lot_split = mz_lot.split('-')

                    mz = mz_lot_split[0]
                    lt = mz_lot_split[1]



            if mz_lot:
                domain_order = [
                    ('company_id', '=', record.company_id.id),
                    ('mz_lot', '=', mz_lot),
                    ('state', 'in', ['done', 'sale']),
                    ('stage_land', '!=', 'cancel')
                ]

                if objectx._name == 'sale.order':
                    domain_order.append(('id', '!=', objectx.id))



                exist = self.env['sale.order'].search(domain_order)

                #raise ValueError([mz, lt, object, mz_lot, exist])



                if exist:

                    raise ValueError(f'YA EXISTE UNA COTIZACION-VENTA PARA {mz_lot} {objectx} {objectx.order_id}  {objectx.order_id.name}')
                    raise ValidationError(f'YA EXISTE UNA COTIZACION-VENTA PARA {mz_lot} {objectx} {objectx.order_id}')
                else:
                    lt = int(lt)
                    if lt <= 9:
                        lt = str(lt).zfill(2)
                        mz_lot = f'{mz}-{lt}'

                    domain_order = [
                        ('company_id', '=', record.company_id.id),
                        ('mz_lot', '=', mz_lot),
                        ('state', 'in', ['done', 'sale']),
                        ('stage_land', '!=', 'cancel')
                    ]

                    if objectx._name == 'sale.order':
                        domain_order.append(('id', '!=', objectx.id))

                    exist = self.env['sale.order'].search(domain_order)

                    # raise ValueError([mz, lt, object, mz_lot, exist])

                    if exist:
                        raise ValidationError(f'YA EXISTE UNA COTIZACION - VENTA PARA {mz_lot}')





            if mz and lt:
                domain_move = [
                    ('company_id', '=', record.company_id.id),
                    ('mz_land_separation_id.name', '=', mz),
                    ('lot_land_separation_id.name', '=', lt),
                    ('state', 'in', ['posted']),
                    # ('stage_land', '!=', 'cancel')
                ]

                if objectx._name == 'account.move':
                    domain_move.append(('id', '!=', objectx.id))

                if objectx._name == 'sale.order.line':
                    if objectx.order_id.move_separation_land_id:
                        domain_move.append(('id', '!=', objectx.order_id.move_separation_land_id.id))

                if objectx._name == 'sale.order':
                    if objectx.move_separation_land_id:
                        domain_move.append(('id', '!=', objectx.move_separation_land_id.id))

                exist_move = self.env['account.move'].search(domain_move)

                if exist_move:
                    raise ValidationError(f'YA EXISTE UNA SEPARACION PARA {mz_lot} ')

    def write(self,values):
        res = super().write(values)


        if  'report_lot_land_line_id' in values and not self.order_line:
            if self.report_lot_land_line_id:

                amount_total = self.report_lot_land_line_id.price

                if self.inicial_lot_set > 0:
                    amount_total -= self.inicial_lot_set

                self.order_line += self.env['sale.order.line'].new({
                    'product_id': self.report_lot_land_line_id.product_tmp_id.product_variant_ids.id,
                    'price_unit': amount_total / self.report_lot_land_line_id.product_tmp_id.dues_qty,
                    'product_uom_qty': self.report_lot_land_line_id.product_tmp_id.dues_qty

                })

            if self.inicial_lot_set and self.report_lot_land_line_id:
                if self.inicial_lot_set > 0:
                    self.order_line += self.env['sale.order.line'].new({
                        'product_id': self.report_lot_land_line_id.product_tmp_id.optional_product_ids[
                            0].product_variant_ids.id,
                        'price_unit': self.inicial_lot_set,
                        'product_uom_qty': 1
                    })




        return res


    @api.model
    def create(self,vals):
        res = super().create(vals)

        #res.check_adelanto()

        return res


    def check_adelanto(self):
        for record in self:

            line_set = None
            amount_set = None

            if record.move_separation_land_id:
                if len(record.order_line) == 2:
                    for line in record.order_line:
                        if line.product_id.is_advanced_land:

                            product_id = record.move_separation_land_id.invoice_line_ids[0].product_id

                            clone_line = line.copy(default={
                                'order_id': record.id ,
                                'product_id': product_id.id ,
                                'tax_id': [(6,0, product_id.taxes_id.ids)]
                            })
                            clone_line.price_unit = record.move_separation_land_id.amount_total

                            price_unit_new = line.price_unit -  record.move_separation_land_id.amount_total
                            line.price_unit =  price_unit_new * 1

                            line_set = line
                            amount_set = price_unit_new * 1

                            record.move_separation_land_id.stage_separation_land = 'initial'

                            #raise ValueError(line.price_unit)



            if line_set:
                line_set.price_unit = amount_set

                #raise ValueError(line_set.price_unit)
            #raise ValueError(line_set)


    def _get_invoiceable_lines(self, final=False):

        if self.sale_line_payment_id:
            return self.sale_line_payment_id



        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        quantity_lines_invoice = 0

        have_separation = False

        for line in self.order_line:
            if line.display_type == 'line_section':
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    continue

            if line.product_id.is_separation_land:
                have_separation = True

            quantity_lines_invoice += 1


        for line in self.order_line:



            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            #if quantity_lines_invoice > 1 and line.product_id.payment_land_dues:
            #    continue

            if have_separation and not line.product_id.is_separation_land:
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)

        res = self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)



        return res


    def _prepare_invoice(self):
        self.get_last_payment_date_land()
        res = super()._prepare_invoice()
        #if self.journal_import_id:
        #    res['journal_id'] = 10

        if self.journal_id:
            res['journal_id'] = self.journal_id.id

        if self.days_expired_land:
            res['days_expired_land'] = self.days_expired_land
            res['value_mora_land'] = self.value_mora_land

        #if self.mz_land:
        #    mz = self.env['product.attribute.value'].search(
        #        [('attribute_id.type_land', '=', 'mz'), ('name', '=', self.mz_land)])
        #    if mz:
        #        res['mz_land_separation_id'] = mz.id


        #if self.lot_land:
        #    lt = self.env['product.attribute.value'].search(
        #        [('attribute_id.type_land', '=', 'lot'), ('name', '=', self.lot_land)])
        #    if lt:
        #        res['lot_land_separation_id'] = lt.id


        #if self.sector_land:
        #    st = self.env['product.attribute.value'].search(
        #        [('attribute_id.type_land', '=', 'stage'), ('name', '=', self.sector_land)])
        #    if st:
        #        res['sector_land_separation_id'] = st.id







        #if self.invoice_payment_import_id:
        #    res['invoice_payment_term_id'] = self.invoice_payment_import_id

        #if self.invoice_date_import:
        #    res['invoice_date'] = self.invoice_date_import

        return res


    def action_confirm(self):
        self.verifi_mz_lot()
        self.check_adelanto()
        res = super().action_confirm()
        if self.move_separation_land_id:
            for line in self.order_line:
                for linex in self.move_separation_land_id.invoice_line_ids:
                    if linex.product_id == line.product_id and line.price_unit == linex.price_unit :
                        line.invoice_lines = [(4, linex.id)]
                        #self.move_separation_land_id.is_separation_land = False


        return res






