from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta , date
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
    qty_dues_payment     = fields.Integer(compute='get_qty_dues_payment', string="Cuotas Pagadas")
    value_due_land       = fields.Float(string="Precio Cuota",copy=False,compute='get_amount_prices_land',digits=(12, 3))
    value_due_land_custom = fields.Float(string="Precio Cuota Custom", copy=False,  digits=(12, 3))

    total_dues_independence = fields.Integer(compute='get_qty_dues_payment', string="Total Independización",store=True)
    qty_dues_independence_payment = fields.Integer(compute='get_qty_dues_payment', string="N° Independización Pagadas",store=True)
    diff_dues_independence = fields.Integer(compute='get_qty_dues_payment', string="N° Independización Pendientes",store=True)

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
    last_date_to_pay_land  = fields.Date(string="Ultima Fecha a Pagar",compute="get_last_payment_date_land",store=True)
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
    schedule_land_custom_ids = fields.One2many('schedule.dues.land.custom', 'order_id',string='Cuotas Personalizada')
    mz_land = fields.Char(store=True,string="Manzana Terreno")
    lot_land = fields.Char(store=True,string="Lote Terreno")
    sector_land = fields.Char(store=True, string="Etapa Terreno")
    m2_land = fields.Char(string="AREA (m2)")

    total_payment_land = fields.Float(string='Total Pagado Cuotas')
    saldo_payment_land = fields.Float(string='Saldo Cuotas')
    total_independence_land = fields.Float(string='Total Pagado Independización')
    saldo_independence_land = fields.Float(string='Saldo Independización')
    saldo_total_land = fields.Float(string='Saldo Terreno')


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


    inicial_lot_set = fields.Float(string="Inicial")
    price_m2 = fields.Float(string='Precio M2',digits=(12, 3))

    documents_document_land_id = fields.Many2one('documents.document',string="Contrato Plantilla",
                                                 domain="[('mimetype','ilike','word')]")
    contrato_generado_land = fields.Binary(string='Contrato Generado')
    name_contrato_generado_land = fields.Char()



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



    @api.depends('order_line', 'order_line.price_unit', 'order_line.product_uom_qty',
                 'order_line.invoice_lines','order_line.invoice_lines.quantity','order_line.qty_invoiced','nro_internal_land')
    def get_qty_dues_payment(self):

        for record in self:
            cantidad_facturada = 0
            total_dues_independence = 0
            qty_dues_independence_payment = 0
            for line in record.order_line:

                if line.product_id.is_independence:
                    total_dues_independence += line.product_uom_qty

                for line_inv in line.invoice_lines:

                    if line_inv.move_id.state == 'cancel':
                        continue

                    if line_inv.move_id.l10n_pe_edi_reversal_type_id:
                        continue

                    if line_inv.move_id.payment_state == 'reversed':
                        continue

                    if not line_inv.move_id.debit_origin_id:

                        if line.product_id.is_independence:

                            qty_dues_independence_payment += line_inv.quantity
                            #line.qty_invoiced

                        if line.product_id.payment_land_dues:
                            cantidad_facturada += line_inv.quantity

                        # qty += line.qty_invoiced





            record.qty_dues_payment = cantidad_facturada

            record.total_dues_independence = total_dues_independence
            record.qty_dues_independence_payment = qty_dues_independence_payment
            record.diff_dues_independence = total_dues_independence - qty_dues_independence_payment


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







    @api.depends('order_line', 'invoice_ids', 'invoice_ids.state','date_first_due_land','date_first_due_land')
    def update_schedule(self):
        for record in self:

            #si tiene fecha de inicio del cronograma

            if record.date_first_due_land:

                record.get_amount_prices_land()

                qty_dues = record.dues_land
                total_dues = record.price_credit_land
                #price_unit = record.value_due_land
                invoice_lines , invoice_lines_initial , qty_to_indepenced , invoice_lines_indepen , amount_indepenced = record.invoice_lines_available_land()

                #PARA INDEPENDIZACION
                schedule_land_indepen = self.env['schedule.dues.land'].search([
                    ('type_schedule','=','independence'),('order_id','=',record.id)
                ])

                if schedule_land_indepen:
                    if len(schedule_land_indepen) < qty_to_indepenced:
                        for lineinde in schedule_land_indepen:
                            lineinde.unlink()
                        schedule_land_indepen = None


                if schedule_land_indepen:
                    c = 0
                    for sche in schedule_land_indepen:
                        dx = {
                            'number_due' : c + 1 ,
                            'date': None ,
                            'balan': 0 ,
                            'amount': amount_indepenced ,
                            'is_paid' : False ,
                            'line_move_id': False ,
                            'invoice_date': False ,
                            'nro_internal_land': False ,
                            'type_schedule': 'independence' ,
                            'sequence': 0
                        }
                        sche.write(dx)
                        c += 1

                else:
                    #crear
                    if qty_to_indepenced > 0:

                        for i in range(int(qty_to_indepenced)):
                            dx = {
                                'number_due' : i + 1 ,
                                'type_schedule': 'independence',
                                'amount': amount_indepenced ,
                                'sequence': 0
                            }
                            record.schedule_land_ids += self.env['schedule.dues.land'].new(dx)


                schedule_land_indepen = self.env['schedule.dues.land'].search([
                    ('type_schedule','=','independence'),('order_id','=',record.id)
                ])

                c = 0
                datex_indepen = record.date_first_due_land

                for inv_line in invoice_lines_indepen:

                    if c + 1 > len(schedule_land_indepen):
                        continue

                    schedule_land_indepen[c].write({
                        'is_paid': True ,
                        'line_move_id': inv_line.id ,
                        'date': inv_line.move_id.date ,
                    })
                    datex_indepen = inv_line.move_id.date


                    c += 1


                schedule_land_indepen = self.env['schedule.dues.land'].search([
                    ('type_schedule','=','independence'),('order_id','=',record.id)
                ])

                if schedule_land_indepen and datex_indepen:
                    i = 0

                    for sche in schedule_land_indepen:

                        if sche.date:
                            continue

                        #predecir la siguiente fecha futura
                        datex_indepen = datex_indepen +  relativedelta(months=1)
                        if datex_indepen.day > 24:
                            datex_indepen = datetime(year=datex_indepen.year, month=datex_indepen.month, day=1, hour=10) +  relativedelta(months=1)
                            datex_indepen = datex_indepen - timedelta(days=1)

                        sche.write({
                            'date': datex_indepen ,
                            #'balan': total_dues - (i*record.value_due_land) ,
                            #'amount': record.value_due_land
                        })
                        i += 1


                #########
                #CUOTAS

                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('type_schedule','=','dues'),('order_id','=',record.id)
                ])

                if schedule_land_dues:
                    c = 0
                    for sche in schedule_land_dues:
                        dx = {
                            'number_due' : c + 1 ,
                            'date': None ,
                            'balan': 0 ,
                            'amount': 0 ,
                            'is_paid' : False ,
                            'line_move_id': False ,
                            'invoice_date': False ,
                            'nro_internal_land': False ,
                            'type_schedule': 'dues'
                        }
                        sche.write(dx)
                        c += 1

                else:
                    #crear cuotas
                    if qty_dues > 0:

                        for i in range(int(qty_dues)):
                            dx = {
                                'number_due' : i + 1 ,
                                'type_schedule': 'dues',
                                'amount': record.value_due_land
                            }
                            record.schedule_land_ids += self.env['schedule.dues.land'].new(dx)


                schedule_land_dues = self.env['schedule.dues.land'].search([
                    ('type_schedule','=','dues'),('order_id','=',record.id)
                ])

                #crear las fechas previstas y balances
                datex = record.date_first_due_land
                i = 0

                value_due = record.value_due_land
                amount_acumulado = 0

                for sche in schedule_land_dues:

                    if record.schedule_land_custom_ids:

                        dx_due = {
                            'date': datex,
                            'balan': total_dues - amount_acumulado,
                            'amount': record.value_due_land_custom
                        }

                        due_custom = self.env['schedule.dues.land.custom'].search([
                            ('order_id','=',record.id),('number_due','=',sche.number_due)
                        ])
                        if due_custom:
                            dx_due.update({
                                'amount': due_custom.amount
                            })

                        amount_acumulado += dx_due['amount']

                        sche.write(dx_due)
                    else:
                        sche.write({
                            'date': datex,
                            'balan': total_dues - (i * value_due),
                            'amount': value_due
                        })




                    i += 1

                    #predecir la siguiente fecha futura

                    datex = datex +  relativedelta(months=1)

                    if datex.day > 24:
                        datex = datetime(year=datex.year, month=datex.month, day=1, hour=10) +  relativedelta(months=1)
                        datex = datex - timedelta(days=1)

                #schedule_land_dues = self.env['schedule.dues.land'].search([
                #    ('type_schedule','=','dues'),('order_id','=',record.id)
                #])

                #rellenar las facturas secuencialmente

                c = 0

                for inv_line in invoice_lines:
                    schedule_land_dues[c].write({
                        'is_paid': True ,
                        'line_move_id': inv_line.id
                    })

                    c += 1

                ## FIN DE CUOTASS


                #para adelantos
                #raise ValidationError(str(invoice_lines_adelanto))


                invoice_lines_adelanto = []

                for factura in record.invoice_ids:
                    for factura_line in factura.invoice_line_ids:
                        if  factura_line.number_advance_land > 0:
                            invoice_lines_adelanto.append(factura_line)

                if invoice_lines_adelanto:
                    for inv_line_ade in invoice_lines_adelanto:
                        #rellenar adelantos
                        df = [
                            ('order_id','=',record.id),
                            ('line_move_id', '=', inv_line_ade.id),
                            ('type_schedule','=','advances')
                        ]
                        exist_line = self.env['schedule.dues.land'].search(df)

                        if inv_line_ade.order_advance_land :
                            if inv_line_ade.order_advance_land != record:
                                if exist_line:
                                    exist_line.unlink()
                                continue



                        dx = {
                            'number_due': inv_line_ade.number_advance_land,
                            'date': inv_line_ade.invoice_date,
                            'balan': 0,

                            'is_paid': True,
                            'line_move_id': inv_line_ade.id,
                            'order_id': record.id ,
                            'type_schedule': 'advances'
                        }


                        if not exist_line:
                            # raise ValueError([dx,exist_line])

                            record.schedule_land_ids += self.env['schedule.dues.land'].create(dx)

                        else:
                            if exist_line.line_move_id and not exist_line.date:
                                exist_line.date = exist_line.line_move_id.move_id.date

                        # else:
                        #    exist_line.write(dx)

                domainx = [
                    ('type_schedule','=','advances'),('order_id','=',record.id),
                    ('line_move_id', '=', False)
                ]

                #eliminar los adelantos sin factura relacionada
                unlink_empty_advance = self.env['schedule.dues.land'].search(domainx)

                if unlink_empty_advance:
                    unlink_empty_advance.unlink()


                #Añadir iniciales:
                if invoice_lines_initial:
                    for inv_inicial in invoice_lines_initial:
                        df = [
                            ('order_id','=',record.id),
                            ('line_move_id', '=', inv_inicial.id),
                            ('type_schedule','=','initial')
                        ]
                        exist_line = self.env['schedule.dues.land'].search(df)

                        dx = {
                            'number_due': 0,
                            'date': inv_inicial.move_id.invoice_date,
                            'balan':  inv_inicial.price_total,
                            'amount': inv_inicial.price_total,
                            'is_paid': True,
                            'line_move_id': inv_inicial.id,
                            'order_id': record.id ,
                            'type_schedule': 'initial'

                        }

                        if not exist_line:
                            # raise ValueError([dx,exist_line])

                            record.schedule_land_ids += self.env['schedule.dues.land'].create(dx)
                        else:
                            exist_line.write(dx)



                #ELIMINAR INICIALES

                domainx = [
                    ('type_schedule','=','initial'),('order_id','=',record.id),
                    ('line_move_id', '=', False)
                ]

                #eliminar los adelantos sin factura relacionada
                unlink_empty_iniciales = self.env['schedule.dues.land'].search(domainx)

                if unlink_empty_iniciales:
                    unlink_empty_iniciales.unlink()






            record.update_credit_saldo()


        self.get_last_payment_date_land()
        self._get_stage_payment_land()
        self.get_amount_prices_land()


    @api.depends('invoice_ids','invoice_ids.state','date_first_due_land','date_first_due_land','type_periodo_invoiced')
    def get_last_payment_date_land(self):
        for record in self:

            #ultima fecha de pago
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
            record.last_payment_date_land = date




            date_next = None

            dues_payment = record.qty_dues_payment
            last_date_to_pay = None

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

                last_due_landx = self.env['schedule.dues.land'].search(
                    [
                        #('is_paid', '!=', True),
                        ('order_id', '=', record.id),
                        #('date', '<=', date_now),
                        ('type_schedule', '=', 'dues')
                    ], order='date desc',limit=1
                )

                if last_due_landx:
                    last_date_to_pay = last_due_landx.date





            record.next_payment_date_land = date_next

            diff_month = 0
            diff_days = 0

            if date_next:

                if date_now > date_next:
                    diff_days = (date_now - date_next).days

                #raise ValueError([diff_days,date_now,date_next,date_now - date_next])



            if date_next : #and record.qty_dues_payment > 0
                #diff_month = ((date_now - date_next).days) / 30
                #hay que cambiar este calculo
                #diff_month += 1
                diff_month = self.env['schedule.dues.land'].search_count(
                    [
                        ('is_paid','!=',True),
                        ('order_id','=',record.id),
                        ('date','<=',date_now),
                        ('type_schedule','=','dues')
                    ]
                )

            #if date_next and record.qty_dues_payment == 0:
            #    raise ValueError([date_now,date_next])
            #    diff_month = ((date_now - date_next).days) / 30
            #raise ValueError(diff_month)



            record.mounth_expired_land = int(diff_month) if diff_month > 0 else 0
            record.amount_payment_month_land =  record.mounth_expired_land * record.value_due_land


            diff_days -= record.days_tolerance_land

            if diff_days < 0:
                diff_days = 0



            record.days_expired_land = diff_days
            record.mora_acumulada  = diff_days * record.value_mora_land
            record.amount_total_payment_month_land = record.amount_payment_month_land + record.mora_acumulada
            record.last_date_to_pay_land = last_date_to_pay


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


            #ESTADO INICIAL O SEPARACION

            if total_initial  > 0 :
                if total_initial_invoiced < total_initial:

                     #SI EXISTE UN MONTO  SEPARADO
                     if total_separation_invoiced > 0:
                         stage = 'separation'

                     #SI TIENE SEPARACION Y TAMBIEN ANTICIPO DE INICIAL (POR VER SI ES ANTICIPO DE INCIAL)
                     if total_separation_invoiced  and total_anticipo_invoiced > 0:
                         stage = 'initial'
                     #SI TIENE INICIAL PAGADAS
                     if total_initial_invoiced > 0:
                         stage = 'initial'


            if total_dues > 0:

                if total_dues_invoiced < total_dues:
                    stage = 'dues'

                if total_dues_invoiced > 0:
                    stage = 'payment'

                if total_dues_invoiced == total_dues:
                    stage = 'completed'


            record.stage_payment_lan = stage





















