import base64
import unicodedata
import os
import time
import io
from io import StringIO
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import fields, api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError


DRAFT = 'draft'
VALIDATED = 'validated'
DECLARED = 'declared'
STATE_SELECTION = [(DRAFT, 'Borrador'), (VALIDATED, 'Validado'), (DECLARED, 'Declarado')]


class KardexElectronicoSunat(models.Model):
    _name = 'kardex.electronico.sunat'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'report.report_xlsx.abstract']
    _description = "Kardex valorizado"

    company_id = fields.Many2one('res.company', string='Empresa', required=True, default=lambda self: self.env.company)
    date_start = fields.Date(string='Fecha desde', required=True)
    date_end = fields.Date(string='Feha hasta', required=True)
    kardex_line_id = fields.One2many('kardex.electronico.sunat.line', 'kardex_id', string='Kardex')
    txt_filename = fields.Char(string="File name")
    txt_binary = fields.Binary(string="File")
    date_generate = fields.Date(string='Fecha de generacion', default=fields.Date.context_today)
    name = fields.Char(string="Nombre")
    state = fields.Selection(selection=STATE_SELECTION, string='Estado', default=DRAFT, tracking=True)

    @api.model
    def action_create_ple_config(self):
        self.env['ple.configuration'].action_create_ple_config('13.1')
    @api.model
    def create(self, vals):
        res = super(KardexElectronicoSunat, self).create(vals)
        res.update({'name': self.env['ir.sequence'].next_by_code('report.ple.13')})
        return res


    def _cost_promedio(self, product, desde, hasta):
        sql = """   SELECT SUM(svl.quantity) as totalcantidades, SUM(svl.value) as totalvalor, round((SUM(svl.value) / SUM(svl.quantity))::numeric,3) as promedio
                    FROM stock_valuation_layer as svl
                    where svl.product_id = %s and 
                    svl.create_date BETWEEN '%s' AND '%s' """ % (product, desde, hasta)
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        cost = 0
        for r in results:
            cost = r.get('promedio') or 0.00
        return cost

    def _generate_line(self, kl):
        period = kl.period.replace('-', '') + '00'
        if kl.stock_quantity_out != 0:
            stock_quantity_out = kl.stock_quantity_out
        else:
            stock_quantity_out = '0.00'

        if kl.unit_cost_out != 0:
            unit_cost_out = kl.unit_cost_out
        else:
            unit_cost_out = '0.00' 

        fecha = kl.date_document_issue.strftime('%d/%m/%Y') or ''

        line = {
            1: period or '',
            2: kl.cuo or '',
            3: kl.number_correlative_cuo or '',
            4: kl.code_establishment or '',
            5: kl.code_table13 or '',
            6: kl.type_exist or '',
            7: kl.code_exist or '',
            8: kl.code_exist_catg13 or '',
            9: kl.code_exist_CUB or '',
            10: fecha,
            11: kl.type_document_transfer_intern or '',
            12: kl.number_serie or '',
            13: kl.number_document_transfer or '',
            14: kl.type_operation or '',
            15: kl.description_exist or '',
            16: kl.code_uom_sunat or '',
            17: kl.code_metod_valuation or '',
            18: kl.stock_quantity_in or '0.00',
            19: kl.unit_cost_in or '0.00',
            20: kl.cost_total_in or '0.00',
            21: stock_quantity_out or '0.00',
            22: unit_cost_out or '0.00',
            23: kl.cost_total_out or '0.00',
            24: kl.unit_quantity_final or '0.00',
            25: kl.cost_unit_final or '0.00',
            26: kl.cost_total_final or '0.00',
            27: kl.state_operation or '1',
            28: kl.other or '',
        }
        return line

    def generate_ekardex_sunat_txt(self):
        str_fin_linea = '\n'
        str_fin ='|'
        str_ruta = ''
        year = self.date_start.year
        month = self.date_start.month
        if len(str(month)) == 1:
            month = '0'+str(month)
        if not self.company_id.vat:
            raise UserError(_("Primero se debe registrar el RUC de la compañía ")+self.company_id.name)

        str_nombre_archivo=''.join(['LE',self.company_id.vat,str(year),str(month),'00','130100','00','1','1','1','1',".txt"])

        contend = ''
        
        for kl in self.kardex_line_id:
            line_vals = self._generate_line(kl).values()
            str_linea_1 = ''
            for val in line_vals:
                str_linea_1 = ''.join(
                    [str_linea_1, str(val), str_fin]
                )
            contend = contend + u''.join(
                [str_linea_1, str_fin_linea])

        if str_ruta:
            if not os.path.exists('/tmp'):
                os.makedirs(str_ruta)
        str_ruta_archivo = os.path.join('/tmp' or '', str_nombre_archivo)
        #str_ruta_archivo = os.path.join('C:/Users/USUARIO/Downloads' or '', str_nombre_archivo)
        fichero = open(str_ruta_archivo, "w")
        fichero.write(contend)
        fichero.close()
        file = open(str_ruta_archivo, "rb")
        out = file.read()

        self.write({
            'txt_filename': str_nombre_archivo,
            'txt_binary': base64.b64encode(out),
            'date_generate': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        })               

    def fill_line_kardex(self):
        company_id = self.company_id
        lgt = len(str(self.date_start.month))
        period = str(self.date_start.year) + '-' + str(self.date_start.month)
        if lgt ==1:
            period = str(self.date_start.year) + '-' + '0' + str(self.date_start.month)
        product_id = False
        product_id_compare = False
        dias = timedelta(days=1)
        to_date= self.date_start - dias
        str_date = to_date.strftime('%Y-%m-%d')
        kardex_electronico_sunat_line_obj = self.env['kardex.electronico.sunat.line']
        values = {}
        # Delete lines if exist
        if len(self.kardex_line_id) > 0:
            for s in self.kardex_line_id:
                s.unlink()

        date_end = self.date_end
        date_end = (date_end + relativedelta(days=1)) - relativedelta(seconds=1)
        date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')

        query = """ ((SELECT
                    sm.product_id producto,			
                    sm.id move_id,
                    sp.name picking,
                    sm.origin origen,
                    sp.scheduled_date fecha,
                    sp.id picking_id,
  					dt.name tipo,
  					split_part(ainv.l10n_latam_document_number, '-', 1) serie,
                    split_part(ainv.l10n_latam_document_number, '-', 2) correlativo,
                    ainv.id invoice_id,
                    --ainv.l10n_pe_edi_operation_type operacion,
  					st.name operacion,
  					sm.name movimiento,
                    uom.l10n_pe_edi_measure_unit_code udm, 
  					COALESCE (pol.price_unit,0.00) price_unit,
                    sm.product_qty,
                    sl1.usage tipo_origen,
                    sl2.usage tipo_destino,
                    'entrada' tipo_a
                    from stock_move sm
                    join stock_location sl1 on sm.location_id = sl1.id
                    join stock_location sl2 on sm.location_dest_id = sl2.id
                    left join stock_picking sp on sm.picking_id = sp.id
                    left join catalog_element st on sp.tabla12 = st.id 
                    left join purchase_order_line pol on sm.purchase_line_id = pol.id
                    left join account_move_line pinvl on pol.id=pinvl.purchase_line_id
                    left join uom_uom uom on pinvl.product_uom_id = uom.id
					left join product_unspsc_code puc on uom.unspsc_code_id = puc.id
                    left join account_move ainv on pinvl.move_id = ainv.id
                    left join account_journal  aj on ainv.journal_id = aj.id
                    left join l10n_latam_document_type dt on ainv.l10n_latam_document_type_id = dt.id
                    left join product_product pp on pp.id = sm.product_id
                    left join product_template pt on pp.product_tmpl_id = pt.id
                    where sm.company_id = %s
                    and sm.state = 'done'
                    and sl2.usage = 'internal'
                    and sp.scheduled_date BETWEEN '%s' AND '%s'
                    and pt.type = 'product'
                    order by sm.date) 
                    UNION 
                    (select
                    sm.product_id producto,
                    sm.id move_id,
                    sp.name picking, 
                    sm.origin origen, 
                    sp.scheduled_date fecha,
                    sp.id picking_id,
					dt.name tipo,
					seq.prefix serie,   
                    split_part(ainv.name, seq.prefix, 2) correlativo,
                    ainv.id invoice_id,
					--ainv.l10n_pe_edi_operation_type operacion,
					st.name operacion,
					sm.name movimiento,
                    uom.l10n_pe_edi_measure_unit_code udm, 
                    COALESCE (pol.price_unit,0.00) price_unit,
                    sm.product_qty,
                    sl1.usage tipo_origen,
                    sl2.usage tipo_destino,
                    'salida' tipo_a
                    from stock_move sm
                    join stock_location sl1 on sm.location_id = sl1.id
                    join stock_location sl2 on sm.location_dest_id = sl2.id
                    left join stock_picking sp on sm.picking_id = sp.id
                    left join catalog_element st on sp.tabla12 = st.id 
                    left join sale_order_line pol on sm.sale_line_id = pol.id
                    left join sale_order_line_invoice_rel solin on pol.id = solin.order_line_id
                    left join account_move_line pinvl on solin.invoice_line_id=pinvl.id
                    left join uom_uom uom on pinvl.product_uom_id = uom.id
                    left join account_move ainv on pinvl.move_id = ainv.id
                    left join account_journal  aj on ainv.journal_id = aj.id
                    left join ir_sequence seq on aj.secure_sequence_id = seq.id
                    left join l10n_latam_document_type dt on ainv.l10n_latam_document_type_id = dt.id
                    left join product_product pp on pp.id = sm.product_id
                    left join product_template pt on pp.product_tmpl_id = pt.id
                    where sm.company_id = %s
                    and sm.state = 'done'
                    and sl1.usage = 'internal'
                    and sp.scheduled_date BETWEEN '%s' AND '%s'
                    and pt.type = 'product'
                    order by sm.date))
                    order by producto, fecha""" %(self.company_id.id, self.date_start, date_end,
                                        self.company_id.id, self.date_start, date_end,)
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        # total_cantidad = 0
        # standard_price = 0
        # costo_total=0
        # if qty_init == 0:
        #     standard_price=0
        #     total_init=0
        #     prom_price=0
        #     costo_total=0
        # else:
        #     standard_price = price_used
        #     total_init = standard_price * qty_init
        #     total_cantidad += qty_init
        #     costo_total=total_init
        #     prom_price=total_init/qty_init

        #Validacion Momentanea para Tipo de Valuacion (Tabla14) PROMEDIO PONDERADO 
        tipo_valuation = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE14'), ('name', '=', '1')]).name
        config_settings = self.env['ple.configuration'].search([('report_type', '=', '13.1'), ('company_id', '=', self.company_id.id)])
        almacen_principal = '0000'
        line = 1
        total_price = 0.00
        contador=1
        cuosm = 'M002-'
        for element in results:
            if product_id_compare != element.get('producto'):
                rel_pro = []
                product_id = element.get('producto')
                product_id_compare = element.get('producto')
                product_id = self.env['product.product'].browse(int(product_id))
                cost_method = product_id.categ_id.property_cost_method
                qq = product_id._compute_quantities_dict(None, None, None, None, str_date)
                qty_init = qq.get(product_id.id).get('qty_available')

                ma_f = (self.date_start - relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                ma_i = (self.date_start - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')

                price_used = self._cost_promedio(product_id.id, ma_i, ma_f)

                total_cantidad = 0
                standard_price = 0
                costo_total=0
                if qty_init == 0:
                    standard_price=0
                    total_init=0
                    prom_price=0
                    costo_total=0
                else:
                    standard_price = price_used
                    total_init = round(standard_price * qty_init, 2)
                    total_cantidad += qty_init
                    costo_total=total_init
                    prom_price=round(total_init/qty_init, 2)

                udm = product_id.uom_id.l10n_pe_edi_measure_unit_code
                if product_id.categ_id.property_cost_method == 'standard':
                    tipo_valuation = config_settings.l10n_pe_standard_valuation_method
                elif product_id.categ_id.property_cost_method == 'fifo':
                    tipo_valuation = config_settings.l10n_pe_fifo_valuation_method
                elif product_id.categ_id.property_cost_method == 'average':
                    tipo_valuation = config_settings.l10n_pe_average_valuation_method
                else:
                    tipo_valuation = "9"

                values.update({
                    'line':str(line),
                    'kardex_id': self.id,
                    'period': period,
                    'cuo': 'A002-'+str(contador),
                    'number_correlative_cuo': 'A1',
                    'code_establishment': almacen_principal,
                    'code_table13': '9',
                    'type_exist': '01',
                    'code_exist': product_id.default_code or '000',
                    'code_exist_catg13':'',
                    'code_exist_CUB': '',
                    'date_document_issue': self.date_start or '',
                    'type_document_transfer_intern': '00',
                    'number_serie': '0',
                    'number_document_transfer': '0',
                    'type_operation': '16',
                    'description_exist': product_id.display_name or '',
                    'code_uom_sunat': udm or '',
                    'code_metod_valuation': tipo_valuation,
                    'stock_quantity_in': qty_init or '0.00',
                    'unit_cost_in': standard_price or '0.00',
                    'cost_total_in': total_init or '0.00',
                    'stock_quantity_out':'0.00',
                    'unit_cost_out':'0.00',
                    'cost_total_out':'0.00',
                    'unit_quantity_final': qty_init or '0.00',
                    'cost_unit_final': prom_price or '0.00',
                    'cost_total_final': costo_total or '0.00',
                    'state_operation':'1',
                    'other':'',
                })
                kardex_electronico_sunat_line_obj.create(values)
                line += 1

            move_id = element.get('move_id')
            cuo = 'M00'+str(contador) or '--'
            tabla5 = '01'
            tabla13 = '09'
            fecha = element.get('fecha')
            tipo = element.get('tipo') or '--'
            serie = element.get('serie') or '--'
            correlativo = element.get('correlativo') or '--'
            operacion = element.get('operacion') or '--'
            picking = element.get('picking')
            medida = element.get('udm') or '--'
            cantidad = element.get('product_qty') or 0
            invoice_id = element.get('invoice_id') or False
            unbuild_id = 0
            campo7 = ''
            entrada = 0
            costo_add = 0
            salida = 0.00
            price_e = 0
            price_s = 0.00
            costo_total_entrada=0
            costo_total_salida=0
            total_unit = 0.00
            costo_final = 0.00
            casop=str('M'+str(contador))
            cas=casop
            sm = self.env['stock.move'].search([('id', '=', str(move_id))])
            tipo = sm.picking_id.tabla10.name

            serie, correlativo, tipo = self.get_data_picking(sm, invoice_id)


            # if sm.picking_id.tabla10.name == '09':
            #     if sm.picking_id.number_document:
            #         if '-' in sm.picking_id.number_document:
            #             serie = sm.picking_id.number_document.split('-')[0]
            #             correlativo = sm.picking_id.number_document.split('-')[1] or ""
            #             tipo = sm.picking_id.tabla10.name

            # if invoice_id:
            #     invoice = self.env['account.move'].browse([invoice_id])
            #     if invoice:
            #         tipo = sm.picking_id.tabla10.name

            #Validaciones
            if serie == '--' and tipo == '--' and correlativo == '--' and operacion == '--': 

                #AJUSTE DE INVENTARIO
                if sm.location_dest_id.usage == 'inventory' and sm.picking_id.name == False:
                    serie = self.env['ir.sequence'].search([('code','=','stock.inventory'),('company_id','=',str(sm.company_id.id))]).prefix or '0000'
                    correlativo = sm.inventory_id.name
                    x = len(serie)
                    correlativo = correlativo[x:] or '0000'
                    tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                    operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '28')]).name
                #SALIDA PRODUCCION
                elif sm.location_dest_id.usage == 'production' and sm.location_id.usage == 'internal':
                    serie = self.env['ir.sequence'].search([('code','=','mrp.production'),('company_id','=',str(sm.company_id.id))]).prefix or '0000'
                    x = len(serie)
                    correlativo = sm.production_id.name_seq
                    if correlativo == False:
                        correlativo = '0000'
                    else:
                        correlativo = correlativo[x:] or '0000'
                    tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                    operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '10')]).name
                #ENTRADA PRODUCCION
                elif sm.location_id.usage == 'production' and sm.location_dest_id.usage == 'internal':
                    serie = self.env['ir.sequence'].search([('code','=','mrp.production'),('company_id','=',str(sm.company_id.id))]).prefix or '0000'
                    x=len(serie)
                    correlativo = sm.production_id.name_seq
                    if correlativo == False:
                        correlativo = '0000'
                    else:
                        correlativo = correlativo[x:] or '0000'
                    tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                    operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '26')]).name
                #DECONSTRUCCION
                elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'internal' and unbuild_id != 0:
                    serie = self.env['ir.sequence'].search([('code','=','mrp.unbuild'),('company_id','=',str(sm.company_id.id))]).prefix or '0000'
                    if serie == '0000':
                        correlativo = '0000'
                    else:
                        correlativo = sm.unbuild_id.name
                        x=len(serie)
                        correlativo = correlativo[x:]
                    tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                    operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '26')]).name
                #ADUANA
                elif sm.location_id.usage == 'supplier' and sm.location_id.name == 'Aduana' and sm.location_dest_id.usage == 'internal':
                    serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                    correlativo = sm.picking_id.number_guia_supplier
                    if correlativo == False:
                            x=len(serie)
                            correlativo = sm.picking_id.name
                            correlativo = correlativo[x:]
                    tipo = sm.picking_id.tabla10.name or '00'
                    operacion = sm.picking_id.tabla12.name or '18'
                #DEVOLUCION DE COMRA
                elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'supplier' and sm.origin_returned_move_id != False:
                    serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                    correlativo = sm.picking_id.number_guia_supplier
                    if correlativo == False:
                        x=len(serie)
                        correlativo = sm.picking_id.name
                        correlativo = correlativo[x:]
                    else:
                        x=len(serie)
                        correlativo = correlativo[x:]
                    tipo = sm.picking_id.tabla10.name
                    operacion = sm.picking_id.tabla12.code
                #DEVOLUCION DE VENTA
                elif sm.location_id.usage == 'customer' and sm.location_dest_id.usage == 'internal' and sm.origin_returned_move_id != False:
                    #serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                    #correlativo = sm.picking_id.number_guia_supplier
                    if correlativo == False:
                            x=len(serie)
                            correlativo = sm.picking_id.name
                            correlativo = correlativo[x:]
                    else:
                        x=len(serie)
                        correlativo = correlativo[x:]
                    tipo = sm.picking_id.tabla10.name
                    operacion = sm.picking_id.tabla12.code
                #ENTRADAS Y SALIDAS SIN FACTURAR
                else:
                    #Transferencias Internas
                    if sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'internal':
                        #serie = sm.picking_id.l10n_latam_document_number.split('-')[0] or '-'
                        #correlativo = sm.picking_id.l10n_latam_document_number.split('-')[1]
                        if correlativo == False:
                            correlativo = 'SN'
                        else:
                            correlativo = sm.picking_id.l10n_latam_document_number.split('-', 1)
                    #Ventas sin facturar
                    elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'customer':
                        #serie = sm.picking_id.picking_type_id.sequence_guia_id.prefix  or '-'
                        #correlativo = sm.picking_id.l10n_latam_document_number.split('-', 1)
                        if correlativo == False:
                            #x=len(serie)
                            correlativo = sm.picking_id.name.split('-', 1)
                    #Compras sin facturar
                    elif sm.location_id.usage == 'supplier' and sm.location_dest_id.usage == 'internal':
                        #serie = sm.picking_id.serie_guia_supplier
                        #correlativo = sm.picking_id.number_guia_supplier
                        serie = "no factura"
                        correlativo = "--"
                    #Default
                    else:
                        serie = sm.picking_id.picking_type_id.sequence_id.prefix or '0000'
                        if serie == '0000':
                            correlativo = '0000'
                        else:
                            correlativo = sm.picking_id.name
                            x=len(serie)
                            correlativo = correlativo[x:] or '0000'
                            
                    operacion = '00' #or sm.picking_id.tabla12.code
                    tipo = '00' #or sm.picking_id.tabla10.name 
            
            #Validacion de UDM
            if medida == '--':
                medida = product_id.uom_id.l10n_pe_edi_measure_unit_code

            #Busqueda de periodos
            ped_l = len(str(fecha.month))
            periodo = str(fecha.year) + '-' + str(fecha.month)
            if ped_l == 1:
                periodo = str(fecha.year) + '-' + '0' + str(fecha.month)

            #Validacion de CUO
            if cuo == '--':
                cuo = str(cuosm + str(contador))
            
            #Validacion de codigo de almacen
            if element.get('tipo_a') == 'entrada':
                sl = self.env['stock.move'].search([('id','=',str(move_id))]).location_dest_id.id
                #almacen = self.env['stock.warehouse'].search([('lot_stock_id.id','=',str(sl))]).code_sunat
                almacen = '0000'
                if almacen == False:
                    #almacen = self.env['stock.warehouse'].search([('company_id.id','=',str(self.company_id.id)),('principal_warehouse','=',True)]).code_sunat
                    almacen = '0000'
            else:
                sl = self.env['stock.move'].search([('id','=',str(move_id))]).location_id.id
                #almacen = self.env['stock.warehouse'].search([('lot_stock_id.id','=',str(sl))]).code_sunat
                almacen = '0000'
                if almacen == False:
                    #almacen = self.env['stock.warehouse'].search([('company_id.id','=',str(self.company_id.id)),('principal_warehouse','=',True)]).code_sunat
                    almacen = '0000'
            #slcad = self.env['stock.landed.cost'].search([('picking_ids','=',picking),('valuation_adjustment_lines.product_id.id','=',str(product_id.id))]).valuation_adjustment_lines
             
            costot=0
            cantidadt=0
            # for s in slcad:
            #     costo = s.additional_landed_cost
            #     costot += costo
            #     cantidad = s.quantity
            #     cantidadt += cantidad

            if costot != 0 and cantidadt != 0:
                costo_add = costot / cantidadt

            # tabla13 = self.env['sunat.table'].search([('id','=',str(tabla13))]).code
            # tabla5 = self.env['sunat.table'].search([('id','=',str(tabla5))]).code

            tabla13 = product_id.product_tmpl_id.catalog_exist.name or '9'
            tabla5 = product_id.product_tmpl_id.type_exist.name or '01'

            if tabla13 == '9':
                campo7 = self.env['stock.move'].search([('id','=',move_id)]).product_id.default_code or ''


            if element.get('tipo_a') == 'entrada': 
                price_e = element.get('price_unit')

                if price_e == 0 and prom_price != 0:
                    price_e = prom_price
                elif price_e == 0 and prom_price == 0:
                    price_e = price_used
               #Validacion de USD a PEN
                picking_purchase = self.env['stock.picking'].search([('name','=',picking)]).origin or '-'
                # if picking_purchase != '-':
                #     moneda_id = self.env['purchase.order'].search([('name','=',picking_purchase)]).currency_id
                #     moneda_soles = company_id.currency_id
                #     if moneda_id != company_id.currency_id:
                #         price_e = moneda_id._convert(price_e,moneda_soles,company_id,fecha)

                entrada = cantidad        
                total_cantidad = total_cantidad + cantidad
                total_price =  total_price + (entrada * price_e)
                costo_total_entrada = (entrada*price_e) + costo_add
                if cost_method == 'fifo':
                    rel_pro.append([entrada,price_e])

                if total_cantidad > 0:
                    costo_final = (entrada*price_e)+costo_total
                    total_unit = costo_final/total_cantidad
                    prom_price = total_unit
                else:
                    total_unit=0
                    costo_final=0
                    prom_price=0

            else:
                price_s = prom_price
                if cost_method == 'fifo':
                    price_s =0
                    solictiado = cantidad
                    for elent in rel_pro:
                        if elent[0] <= solictiado and elent[0] !=0:
                            price_s += elent[0] * elent[1]
                            solictiado -= elent[0]
                            elent[0] = 0

                        if elent[0] > solictiado and elent[0] != 0:
                            price_s += solictiado * elent[1]
                            elent[0] = elent[0] - solictiado
                            break
                        if solictiado == 0:
                            break
                    price_s = price_s/cantidad

                salida = cantidad
                total_cantidad = total_cantidad - cantidad
                total_price = total_price - (entrada * price_e)
                costo_total_salida = (salida * price_s) + costo_add
                if total_cantidad > 0:
                    costo_final = costo_total-(salida*price_s)
                    total_unit = costo_final/total_cantidad
                else:
                    total_unit=0
                    costo_final=0
                    prom_price=0

            if invoice_id:
                line_inv = self.env['account.move.line'].search([('move_id','=',invoice_id),('product_id','=',product_id.id)], limit=1)
                invoice = line_inv.move_id
                #serie, correlativo = self.get_series_correlative(line_inv)
                #tipo = invoice.l10n_latam_document_type_id.code

                if line_inv.move_id.state in ['cancel', 'anulled', 'draft']:
                    continue
                if salida != 0:
                    #price_s = line_inv.price_subtotal/line_inv.quantity or 0.00
                    costo_total_salida = (salida * price_s) + costo_add
                if entrada != 0:
                    price_e = line_inv.price_subtotal/line_inv.quantity or 0.00 
                    costo_total_entrada = (entrada*price_e) + costo_add
            else:
                sm = self.env['stock.move'].search([('id','=',str(move_id))])
                picking_id = sm.picking_id
                if picking_id.sale_id:
                    sale_id = picking_id.sale_id
                    invoice_id = sale_id.mapped('invoice_ids')
                    if invoice_id:
                        if invoice_id.state in ['cancel', 'anulled', 'draft']:
                            continue
                        line_inv = self.env['account.move.line'].search([('move_id','in',invoice_id.ids),('product_id','=',product_id.id)], limit=1)
                        serie, correlativo = self.get_series_correlative(line_inv.move_id)
                        tipo = invoice_id.l10n_latam_document_type_id.code
                        if salida != 0:
                            if line_inv:
                                #price_s = line_inv.price_subtotal/line_inv.quantity or 0.00
                                costo_total_salida = (salida * price_s) + costo_add

                                #serie = invoice_id.journal_id.invoice_sequence_id.prefix
                                #correlativo = invoice_id.number.replace(serie,'')
                                #tipo = invoice_id.l10n_latam_document_type_id.code
                                operacion = invoice_id.journal_id.type_operation_table_12.code
                        # if entrada != 0:
                        #     price_e = line_inv.price_subtotal/line_inv.quantity or 0.00 
                        #     costo_total_entrada = (entrada*price_e) + costo_add
                    

            costo_total_salida = (salida * price_s) + costo_add
            
            if salida == 0:
                salida = '0.00'
            else:
                salida = round(salida,2)
            
            if price_s == 0:
                price_s = '0.00'
            else:
                price_s = round(price_s,2)

            if tipo_valuation =='2':
                total_unit = '0.00'
            else:
                round(total_unit,2) or '0.00'

            costo_final = total_unit * total_cantidad

            costo_total = costo_final
            values.update({
                    'line':str(line),
                    'kardex_id': self.id,
                    'period': periodo,
                    'cuo': cuo,
                    'number_correlative_cuo': cas,
                    'code_establishment': almacen,
                    'code_table13': tabla13,
                    'type_exist': tabla5,
                    'code_exist': campo7 or '000',
                    'code_exist_CUB': '',
                    'date_document_issue': fecha,
                    'type_document_transfer_intern': tipo or '',
                    'number_serie': serie or '',
                    'number_document_transfer': correlativo or '',
                    'type_operation': operacion or '',
                    'description_exist': product_id.display_name or '',
                    'code_uom_sunat': medida or '',

                    'code_metod_valuation': tipo_valuation,
                    'stock_quantity_in': entrada or '0.00',
                    'unit_cost_in': round(price_e,2) or '0.00',
                    'cost_total_in': round(costo_total_entrada,2) or '0.00',
                    'stock_quantity_out':salida,
                    'unit_cost_out': price_s,
                    'cost_total_out': round(costo_total_salida,2) or '0.00',
                    'unit_quantity_final': total_cantidad or '0.00',
                    'cost_unit_final': round(total_unit,2),
                    'cost_total_final': round(costo_final,2) or '0.00',
                    'state_operation':'1',
                    'other':'',
            })
            kardex_electronico_sunat_line_obj.create(values)
            line +=1           
            contador +=1

        values = {}
        self.generate_ekardex_sunat_txt()
        self.write({'state':'validated'})

        return values

    @api.onchange('date_start')
    def _auto_last_day(self):
        if self.date_start:
            start = self.date_start
            end = (start + relativedelta(months=1)) - relativedelta(days=1)
            self.date_end = end
        return


    def action_generate_ple(self, value):
        value.update({'state': 'validated'})
        self.write(value)

    def get_series_correlative(self, move_id):
        if move_id.move_type in ['in_invoice', 'in_refund']:
            name = move_id.l10n_latam_document_number
            return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')
        elif move_id.move_type in ['out_invoice', 'out_refund']:
            name = move_id.name
            return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')
        elif move_id.move_type in ['entry']:
            name = move_id.ref
            return ('', name)


    def get_data_picking(self, sm, invoice_id):
        serie= "--"
        correlativo = "--"
        tipo = ""
        if sm.picking_id.number_document:
            serie = sm.picking_id.number_document.split('-')[0]
            correlativo = sm.picking_id.number_document.split('-')[1] or ""
            tipo = sm.picking_id.tabla10.name

        if invoice_id:
            move_id = self.env['account.move'].browse(invoice_id)
            serie, correlativo = self.get_series_correlative(move_id)
            tipo = move_id.l10n_latam_document_type_id.code
        return (serie,correlativo,tipo)
