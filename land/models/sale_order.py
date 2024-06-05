from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nro_internal_land =  fields.Char(string="Expediente")
    mz_lot            =  fields.Char(string="MZ - LOTE")
    sector            =  fields.Char()
    stage_land           = fields.Selection([
        ('signed',_('Firmado'))  ,
        ('preaviso',_('Carta Preaviso')),
        ('cancel',_('Resuelto o Cancelado'))
    ],string="Estado Terreno")
    dues_land            = fields.Float(string="Cuotas")
    value_due_land       = fields.Float(string="Precio Cuotas")
    crono_land           = fields.Char(string="Crono")
    days_tolerance_land  = fields.Integer(string="Gracia",default=3)
    value_mora_land = fields.Float(string="Precio Mora",default=10)
    percentage_refund_land = fields.Float(string="Porcentaje Devolucion")

    date_sign_land = fields.Date(string="Fecha Firma del Contrato")
    date_first_due_land = fields.Date(string="Fecha Primera Cuota")
    start_date_schedule_land = fields.Date(compute="get_start_date_schedule_land",store=True)

    modality_land = fields.Selection([
        ('single',_('Soltero')) ,
        ('low_customer',_('Baja cliente')) ,
        ('married',_('Casado')) ,
        ('divorcee',_('Divorciado')) ,
        ('confirmer',_('Confirmador')) ,
        ('widow',_('Viudo')) ,
        ('transfer',_('Transferencia')) ,
    ],string="Modalidad")

    obs_modality_land = fields.Text(string="Observaciones")
    price_total_land = fields.Float(string="Valor del Terreno")
    price_initial_land = fields.Float(string="Inicial del Terreno")
    price_credit_land = fields.Float(string="Credito del Terreno")

    note = fields.Text()
    recalcule_and_save_total_land = fields.Boolean(default=True,string="Recalcular Montos")

    seller_land_id = fields.Many2one('seller.land',string="Proveedor Terreno",required=True)


    #esto es para importar
    journal_import_id = fields.Integer()
    price_unit_import = fields.Float()
    invoice_payment_import_id = fields.Integer()
    invoice_date_import =  fields.Date()
    journal_id = fields.Many2one('account.journal',string="Diario")
    move_separation_land_id = fields.Many2one('account.move',string='Factura Separación')

    stage_payment_lan = fields.Selection([
        ('initial','Inicial'),
        ('dues','Cuotas'),
        ('completed','Completada')
    ],compute='_get_stage_payment_land',store=True,string='Etapa Terreno')

    last_payment_date_land = fields.Date(string="Ultima Fecha de Pago",compute="get_last_payment_date_land",store=True)
    next_payment_date_land = fields.Date(string="Proxima Fecha de Pago", compute="get_last_payment_date_land",store=True)
    days_expired_land = fields.Integer(string="Dias Vencidos", compute="get_last_payment_date_land")
    mounth_expired_land = fields.Integer(string="Meses Vencidos", compute="get_last_payment_date_land",store=True)

    type_periodo_invoiced  = fields.Selection([('half_month','Quincenal'),('end_month','Fin de Mes')],
                                              string="Periodo de Facturación")
    #compute='get_start_date_schedule_land

    schedule_land_ids = fields.One2many('schedule.dues.land','order_id')
    mz_land = fields.Char(compute="get_info_land",store=True,string="Manzana Terreno")
    lot_land = fields.Char(compute="get_info_land",store=True,string="Lote Terreno")
    sector_land = fields.Char(compute="get_info_land", store=True, string="Etapa Terreno")
    m2_land = fields.Char(string="AREA (m2)")
    total_payment_land = fields.Float(string='Total Pagado Cuotas')
    saldo_payment_land = fields.Float(string='Saldo Cuotas')
    qty_dues_payment   = fields.Integer(compute='get_qty_dues_payment',string="Cuotas Pagadas")
    commision_lan     = fields.Float(string='Commision Terreno')
    commision_line_ids       = fields.One2many('commission.land.line','sale_id')
    report_lot_land_line_id = fields.Many2one('report.lot.land.line',compute='get_report_lot_land_line_id',store=True)


    def update_dates_land(self):
        for invc in self.invoice_ids:
            if invc.amount_total == self.price_initial_land:
                invc.invoice_date = self.date_sign_land
            #if invc.state != 'draft':
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




    @api.depends('mz_land','lot_land','state','mz_lot','note')
    def get_report_lot_land_line_id(self,product_tmp=None):

        for record in self:
            if not  product_tmp:
                product_tmp = self.env['product.template'].search(
                    [('company_id', '=', record.company_id.id), ('payment_land_dues', '=', True)])
                if not product_tmp:
                    product_tmp = self.env['product.template'].search(
                        [('payment_land_dues', '=', True), ('attribute_line_ids', '!=', False)])

            line = None

            #raise ValueError(product_tmp)

            if record.mz_land and record.lot_land:
                line = self.env['report.lot.land.line'].search([
                    ('mz_value_id.name','=',record.mz_land),
                    ('name','=',str(int(record.lot_land))),
                    ('product_tmp_id','=',product_tmp.id)
                ])
            record.report_lot_land_line_id = line



    def show_dues_land(self):
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
            qty = 0
            for line in record.order_line:
                if line.product_id.payment_land_dues:
                    qty += line.qty_invoiced
            record.qty_dues_payment = qty


    @api.onchange('price_total_land','price_initial_land')
    def onchange_credit(self):
        for record in self:
            record.price_credit_land = record.price_total_land - record.price_initial_land

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
        return

    @api.depends('order_line','mz_lot','sector')
    def get_info_land(self):
        for record in self:
            mz = None
            lt = None
            stage = None
            m2 = None
            for line in record.order_line:
                if line.product_id.manzana and  line.product_id.manzana != '':
                    mz = line.product_id.manzana

                if line.product_id.lote and  line.product_id.lote  != '':
                    lt = line.product_id.lote

                if line.product_id.sector_land and  line.product_id.sector_land  != '':
                    stage = line.product_id.sector_land

                if line.product_id.m2_land and  line.product_id.m2_land  != '':
                    m2 = line.product_id.m2_land

            if record.mz_lot and not mz and not lt:
                mz_lot = record.mz_lot.split('-')
                if len(mz_lot) == 2:
                    mz = str(mz_lot[0])
                    lt = str(mz_lot[1])


            record.mz_land = mz
            record.lot_land = lt

            if not stage and record.sector:
                stage = record.sector

            if stage:
                record.sector_land = stage

            if m2:
                record.m2_land = m2

    @api.depends('order_line', 'invoice_ids', 'invoice_ids.state')
    def update_schedule(self):
        for record in self:
            if record.start_date_schedule_land:
                qty_dues = 0
                total_dues = 0
                price_unit = 0
                qty_invoiced = 0
                total_payment = 0

                for line in record.order_line:
                    if line.product_id.payment_land_dues:
                        qty_dues = line.product_uom_qty
                        total_dues = qty_dues * line.price_unit
                        price_unit = line.price_unit
                        qty_invoiced = line.qty_invoiced

                if not record.schedule_land_ids :


                    if qty_dues > 0:
                        datex = record.start_date_schedule_land
                        for i in range(int(qty_dues)):
                            dx = {
                                'number_due' : i + 1 ,
                                'date': datex ,
                                'balan': total_dues - (i*price_unit) ,
                                'amount': price_unit ,
                                'is_paid' : True if (i + 1) <= qty_invoiced else False
                            }



                            datex = datex +  relativedelta(months=1)

                            if datex.day > 24:
                                datex = datetime(year=datex.year, month=datex.month, day=1, hour=10) +  relativedelta(months=1)
                                datex = datex - timedelta(days=1)





                            try:
                                record.schedule_land_ids += self.env['schedule.dues.land'].new(dx)
                            except:
                                raise ValueError(dx)

                if record.schedule_land_ids :

                    invoices = self.env['account.move'].search([
                        ('id', 'in', record.invoice_ids.ids),
                        ('is_initial_land', '=', False),

                    ], order='invoice_date asc')

                    invoicesx = []
                    for inv in invoices:
                        if inv.is_initial_land:
                            continue
                        invoicesx.append(inv)

                    i = 0
                    for linex in record.schedule_land_ids :
                        linex.update({
                            'is_paid' : True if (i + 1) <= qty_invoiced else False ,

                        })
                        try:
                            linex.update({
                                'move_id': invoicesx[i].id
                            })
                            total_payment += invoicesx[i].amount_due_land

                        except:
                            linex.update({
                                'move_id': False
                            })
                        i += 1

                    record.total_payment_land = round(total_payment,2)
                    record.saldo_payment_land = round( record.price_credit_land - total_payment , 2 )
            record.get_last_payment_date_land()


    @api.depends('date_first_due_land')
    def get_start_date_schedule_land(self):
        for record in self:
            date_start = record.date_first_due_land
            if date_start and date_start.day <= 24 :
                date_start = datetime(year=date_start.year,month=date_start.month,day=15,hour=10)
                date_start = date_start.date()
                record.type_periodo_invoiced = 'half_month'
            if date_start and date_start.day > 24:
                date_start = datetime(year=date_start.year, month=date_start.month, day=1, hour=10) +  relativedelta(months=1)
                date_start = date_start - timedelta(days=1)
                date_start = date_start.date()
                record.type_periodo_invoiced = 'end_month'
            record.start_date_schedule_land = date_start

    @api.depends('invoice_ids','invoice_ids.state','date_first_due_land','date_first_due_land','type_periodo_invoiced')
    def get_last_payment_date_land(self):
        for record in self:
            date_now = fields.Datetime.now().date()
            date = None
            for invoice in record.invoice_ids:
                if invoice.state == 'posted':
                    if invoice.invoice_date:
                        if not date:
                            date = invoice.invoice_date
                        else:
                            if invoice.invoice_date > date:
                                date = invoice.invoice_date

            #    date = record.date_first_due_land + relativedelta(months=1)
            record.last_payment_date_land = date

            diff_month =  0

            if date:
                date1 = date_now
                date2 = date
                diff_month = (date1.year - date2.year) * 12 + (date1.month - date2.month)




            record.mounth_expired_land = diff_month

            date_next = None

            dues_payment = 0
            for line in record.order_line:
                if line.product_id.payment_land_dues:
                    dues_payment = line.qty_invoiced

            if  record.date_first_due_land:

                if dues_payment == 0:
                    dues_payment = 1

                date_next = record.date_first_due_land +  relativedelta(months=dues_payment)

                if date_next.day <= 24 :
                    date_next = datetime(year=date_next.year,month=date_next.month,day=15,hour=10)
                    date_next = date_next.date()
                if date_next.day > 24:
                    date_next = datetime(year=date_next.year,month=date_next.month,day=1,hour=10) +  relativedelta(months=1)
                    date_next = date_next - timedelta( days=1)
                    date_next = date_next.date()

            record.next_payment_date_land = date_next

            diff_days  = 0






            if date_next and date_next < date_now:
                diff_days = (date_now - date_next ).days

            diff_days -= record.days_tolerance_land

            if diff_days < 0:
                diff_days = 0


            record.days_expired_land = diff_days



    @api.depends('order_line','order_line.product_id','order_line.qty_invoiced',
                 'note','invoice_ids','invoice_ids.state','invoice_ids.invoice_date')
    def _get_stage_payment_land(self):
        for record in self:
            stage = None

            total_initial = 0
            total_initial_invoiced = 0

            total_dues = 0
            total_dues_invoiced = 0
            for line in record.order_line:
                if line.product_id.is_advanced_land:
                    total_initial += line.product_uom_qty
                    total_initial_invoiced += line.qty_invoiced

                if line.product_id.payment_land_dues:
                    total_dues += line.product_uom_qty
                    total_dues_invoiced +=   line.qty_invoiced
            if total_initial_invoiced < total_initial :
                stage = 'initial'

            if not stage:
                if total_dues_invoiced < total_dues:
                    stage = 'dues'
                if total_dues_invoiced == total_dues:
                    stage = 'completed'

            record.stage_payment_lan = stage




    def show_m2_land(self):

        object = self.env['product.attribute'].search([('type_land','=','m2')])

        return {
            "name": f"METRADO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.attribute",
            "res_id": object.id,
            "target": "new",


        }

    def _update_text_mz_lote(self):
        for record in self:
            mz =   None
            lote = None
            total = record.amount_total
            dues = 0
            value_due = 0


            credit = 0

            for line in record.order_line:
                if line.product_id.manzana:
                    mz = line.product_id.manzana
                if line.product_id.lote:
                    lote = line.product_id.lote

                if line.product_id.payment_land_dues:
                    credit = line.price_total
                    dues =  line.product_uom_qty
                    value_due = line.price_unit

            inicial = total - credit


            if mz or lote:
                mz_lot = (mz or '') + '-' + (lote or '')

                sql = f'''  UPDATE sale_order 
                            SET mz_lot = '{mz_lot}'  , 
                            price_total_land = {total}  ,
                            price_initial_land  = {inicial} ,
                            price_credit_land = {credit} ,
                            dues_land = {dues} ,
                            value_due_land = {value_due}
                            WHERE id = {record.id}  
                       '''
                self.env.cr.execute(sql)

    def _recalcule_price_land(self):
        for record in self:

            for line in record.order_line:
                if line.product_id and line.product_id.payment_land_dues:

                    line.change_product_uom_qty_land()


    def write(self,values):
        res = super().write(values)
        for record in self:
            if record.recalcule_and_save_total_land:
                record._update_text_mz_lote()

        self.check_adelanto()

        return res

    @api.model
    def create(self,vals):
        res = super().create(vals)
        res.check_adelanto()
        return res


    def check_adelanto(self):
        for record in self:
            if record.move_separation_land_id:
                if len(record.order_line) == 2:
                    for line in record.order_line:
                        if line.product_id.is_advanced_land:
                            clone_line = line.copy(default={'order_id': record.id , 'product_id': record.move_separation_land_id.invoice_line_ids[0].product_id.id })
                            clone_line.price_unit = record.move_separation_land_id.amount_untaxed
                            line.price_unit = line.price_unit - clone_line.price_unit


    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        quantity_lines_invoice = 0
        for line in self.order_line:
            if line.display_type == 'line_section':
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    continue

            quantity_lines_invoice += 1



        for line in self.order_line:



            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if quantity_lines_invoice > 1 and line.product_id.payment_land_dues:
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



        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)


    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        #if self.journal_import_id:
        #    res['journal_id'] = 10

        if self.journal_id:
            res['journal_id'] = self.journal_id.id

        if self.days_expired_land:
            res['days_expired_land'] = self.days_expired_land
            res['value_mora_land'] = self.value_mora_land

        #if self.invoice_payment_import_id:
        #    res['invoice_payment_term_id'] = self.invoice_payment_import_id

        #if self.invoice_date_import:
        #    res['invoice_date'] = self.invoice_date_import

        return res


    def action_confirm(self):
        res = super().action_confirm()
        if self.move_separation_land_id:
            for line in self.order_line:
                for linex in self.move_separation_land_id.invoice_line_ids:
                    if linex.product_id == line.product_id and line.price_unit == linex.price_unit :
                        line.invoice_lines = [(4, linex.id)]
                        #self.move_separation_land_id.is_separation_land = False


        return res






