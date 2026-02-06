# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import calendar,datetime
from datetime import timedelta


class Report13xlxs(models.AbstractModel):
    _name = 'report.kardex.electronico.sunat'
    _description = 'Report ple 13 fisico'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('{}.xlsx'.format('Kardex'))
        bold_right = workbook.add_format({'bold': True, 'font_color': 'black'})
        bold = workbook.add_format({'bold': True, 'font_color': 'black', 'text_wrap': True,'right': True, 'bottom': True, 'top': True})
        normal = workbook.add_format({'font_color': 'black', 'num_format': '#,##0.00'})
        right = workbook.add_format({'font_color': 'black'})
        left = workbook.add_format({'font_color': 'black'})

        bold.set_align('left')
        bold.set_text_wrap()
        normal.set_align('center')
        left.set_align('left')
        right.set_align('right')

        sheet.set_column('A:A', 17)
        sheet.set_column('B:B', 17)
        sheet.set_column('C:C', 17)
        sheet.set_column('D:D', 17)
        sheet.set_column('E:E', 17)
        sheet.set_column('F:F', 17)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 17)
        sheet.set_column('I:I', 17)
        sheet.set_column('J:J', 17)
        sheet.set_column('K:K', 17)
        sheet.set_column('L:L', 17)
        sheet.set_column('M:M', 17)
        sheet.set_column('N:N', 17)


        sheet.merge_range('A1:D1', u'FORMATO 13.1: REGISTRO DE INVENTARIO PERMANENTE VALORIZADO', bold_right)
        #sheet.merge_range('A3:B3', u'PERIODO: {}'.format(obj.range_id.name), bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),
                          bold_right)

        sheet.merge_range('A6:B6', u'Fecha:', bold_right)
        sheet.merge_range('C6:F6', 'fecha desde %s hasta %s' % (fields.Date.to_string(obj.date_start),fields.Date.to_string(obj.date_end)),
                          bold_right)

        sheet.merge_range('A7:D7', u'DOCUMENTO DE TRASLADO, COMPROBANTE DE PAGO, DOCUMENTO INTERNO O SIMILAR', bold)
        sheet.merge_range('E7:E8', u'TIPO DE OPERACIÓN (TABLA 12)', bold)
        sheet.merge_range('F7:H7', u'ENTRADAS', bold)
        sheet.merge_range('I7:K7', u'SALIDAS', bold)
        sheet.merge_range('L7:N7', u'SALDO FINAL', bold)

        sheet.write('A8', u'FECHA', bold)
        sheet.write('B8', u'TIPO (TABLA 10)', bold)
        sheet.write('C8', u'SERIE', bold)
        sheet.write('D8', u'NÚMERO', bold)

        sheet.write('F8', u'CANTIDAD', bold)
        sheet.write('G8', u'COSTO UNITARIO', bold)
        sheet.write('H8', u'COSTO TOTAL', bold)

        sheet.write('I8', u'CANTIDAD', bold)
        sheet.write('J8', u'COSTO UNITARIO', bold)
        sheet.write('K8', u'COSTO TOTAL', bold)

        sheet.write('L8', u'CANTIDAD', bold)
        sheet.write('M8', u'COSTO UNITARIO', bold)
        sheet.write('N8', u'COSTO TOTAL', bold)

        row= 8

        list_date = self.get_list_poermonth_by_date(obj.date_start, obj.date_end)
        for date_u in list_date:
            row= self.set_data_xls(obj, date_u[0], date_u[1], row, sheet, normal)




        row +=1




        # sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL REGISTRO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        # sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        # sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n Y/O PAGO', bold)
        # sheet.merge_range('D7:F7', u'COMPROBANTE DE PAGO \nO DOCUMENTO', bold)
        # sheet.merge_range('D8:D9', u'TIPO', bold)
        # sheet.merge_range('E8:E9', u'Nº SERIE', bold)
        # sheet.merge_range('F8:F9', u'NÚMERO', bold)
        # sheet.merge_range('G7:I7', u'INFORMACION DEL CLIENTE', bold)
        # sheet.merge_range('G8:H8', u'DOCUMENTO DE IDENTIDAD', bold)
        # sheet.write('G9', u'TIPO', bold)
        # sheet.write('H9', u'NUMERO', bold)
        # sheet.merge_range('I8:I9', u'APELLIDOS Y NOMBRES,\nDENOMINACION \nO RAZON SOCIAL', bold)
        #
        # sheet.merge_range('J7:J9', u'VALOR \nFACTURADO \nDE LA \nEXPORTACIÓN', bold)
        # sheet.merge_range('K7:K9', u'BASE \nIMPONIBLE \nDE LA \nOPERACIÓN \nGRAVADA', bold)
        #
        # sheet.merge_range('L7:M8', u'IMPORTE TOTAL \nDE LA OEPRACIÓN \nEXONERADA O INAFECTA', bold)
        # sheet.write('L9', u'EXONERADA', bold)
        # sheet.write('M9', u'INAFECTA', bold)
        #
        # sheet.merge_range('N7:N9', u'ISC', bold)
        # sheet.merge_range('O7:O9', u'IGV Y/O IPM', bold)
        # sheet.merge_range('P7:P9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        # sheet.merge_range('Q7:Q9', u'IMPORTE\nTOTAL DEL \nCOMPROBANTE \nDE PAGO', bold)
        #
        # sheet.merge_range('R7:R9', u'TIPO DE \nCAMBIO', bold)
        #
        # sheet.merge_range('S7:V7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        # sheet.merge_range('S8:S9', u'FECHA', bold)
        # sheet.merge_range('T8:T9', u'TIPO', bold)
        # sheet.merge_range('U8:U9', u'SERIE', bold)
        # sheet.merge_range('V8:V9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)
        # sheet.merge_range('W8:W9', u'ESTADO', bold)
        #
        # i = 9
        # for line in obj.line_ids:
        #     sheet.write(i, 0, line.move_name, normal)
        #     sheet.write(i, 1, line.date_emission, normal)
        #     sheet.write(i, 2, line.date_due, normal)
        #     sheet.write(i, 3, line.document_payment_type, normal)
        #     sheet.write(i, 4, line.document_payment_series or '', normal)
        #     sheet.write(i, 5, line.document_payment_number or '', normal)
        #     sheet.write(i, 6, line.customer_document_type or '', normal)
        #     sheet.write(i, 7, line.customer_document_number or '', normal)
        #     sheet.write(i, 8, line.customer_name, left)
        #     sheet.write(i, 9, line.amount_export or '0.00', right)
        #     sheet.write(i, 10, line.amount_untaxed or '0.00', right)
        #     sheet.write(i, 11, line.amount_tax_exo or '0.00', right)
        #     sheet.write(i, 12, line.amount_tax_ina or '0.00', right)
        #     sheet.write(i, 13, line.amount_tax_isc or '0.00', right)
        #     sheet.write(i, 14, line.amount_tax_igv or '0.00', right)
        #     sheet.write(i, 15, line.amount_tax_other or '0.00', right)
        #     sheet.write(i, 16, line.amount_total or '0.00', right)
        #     sheet.write(i, 17, line.exchange_currency, right)
        #     sheet.write(i, 18, line.date_emission_update, normal)
        #     sheet.write(i, 19, line.document_payment_type_update, normal)
        #     sheet.write(i, 20, line.document_payment_series_update, normal)
        #     sheet.write(i, 21, line.document_payment_correlative_update, normal)
        #     sheet.write(i, 22, line.state_opportunity, normal)
        #     i += 1



    def set_data_xls(self, obj, date_start, date_end, row, sheet, normal):


        products = self.get_prduct_move_by_date(obj, date_start, date_end)
        # if products:
        #     str_date = "Fecha desde %s hasta %s" % (fields.Date.to_string(date_start), fields.Date.to_string(date_end))
        #     sheet.write(row, 1, str_date, normal)
        #     row += 1

        for product in products:
            sheet.write(row, 1, product.name, normal)
            row += 1
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
                                and pp.id = %s
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
                                and pp.id = %s
                                and pt.type = 'product'
                                order by sm.date))
                                order by producto, fecha""" % (obj.company_id.id, date_start, date_end, product.id,
                                                               obj.company_id.id, date_start, date_end, product.id,)
            self.env.cr.execute(query)
            results = self.env.cr.dictfetchall()
            cost_method = product.categ_id.property_cost_method

            dias = timedelta(days=1)
            to_date = date_start - dias

            str_dates = to_date.strftime('%Y-%m-%d')
            qq = product._compute_quantities_dict(None, None, None, None, str_dates)
            qty_init = qq.get(product.id).get('qty_available')

            ma_f = (date_start - relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            ma_i = (date_start - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')

            price_used = self._cost_promedio(product.id, ma_i, ma_f)

            total_cantidad = 0
            standard_price = 0
            costo_total = 0
            if qty_init == 0:
                standard_price = 0
                total_init = 0
                prom_price = 0
                costo_total = 0
            else:
                standard_price = price_used
                total_init = round(standard_price * qty_init, 2)
                total_cantidad += qty_init
                costo_total = total_init
                prom_price = round(total_init / qty_init, 2)

            product_id = product
            udm = product.uom_id.l10n_pe_edi_measure_unit_code
            start_period = str(date_start.strftime("%d/%m/%Y"))

            sheet.write(row, 0, fields.Date.to_string(date_start), normal)
            sheet.write(row, 3, 'Saldo inicial', normal)
            sheet.write(row, 4, '16', normal)

            sheet.write(row, 5, qty_init, normal)
            sheet.write(row, 6, standard_price, normal)
            sheet.write(row, 7, total_init, normal)

            sheet.write(row, 8, 0, normal)
            sheet.write(row, 9, 0, normal)
            sheet.write(row, 10, 0, normal)

            sheet.write(row, 11, qty_init, normal)
            sheet.write(row, 12, prom_price, normal)
            sheet.write(row, 13, costo_total, normal)
            row +=1
            tipo_valuation = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE14'), ('name', '=', '1')]).name
            total_price = 0.00

            rel_pro = []
            for element in results:

                move_id = element.get('move_id')
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
                costo_total_entrada = 0
                costo_total_salida = 0
                total_unit = 0.00
                costo_final = 0.00
                sm = self.env['stock.move'].search([('id', '=', str(move_id))])
                tipo = sm.picking_id.tabla10.name

                serie, correlativo, tipo = self.get_data_picking(sm, invoice_id)
                if serie == '--' and tipo == '--' and correlativo == '--' and operacion == '--':

                    # AJUSTE DE INVENTARIO
                    if sm.location_dest_id.usage == 'inventory' and sm.picking_id.name == False:
                        serie = self.env['ir.sequence'].search([('code', '=', 'stock.inventory'), (
                        'company_id', '=', str(sm.company_id.id))]).prefix or '0000'
                        correlativo = sm.inventory_id.name
                        x = len(serie)
                        correlativo = correlativo[x:] or '0000'
                        tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                        operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '28')]).name
                    # SALIDA PRODUCCION
                    elif sm.location_dest_id.usage == 'production' and sm.location_id.usage == 'internal':
                        serie = self.env['ir.sequence'].search([('code', '=', 'mrp.production'), (
                        'company_id', '=', str(sm.company_id.id))]).prefix or '0000'
                        x = len(serie)
                        correlativo = sm.production_id.name_seq
                        if correlativo == False:
                            correlativo = '0000'
                        else:
                            correlativo = correlativo[x:] or '0000'
                        tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                        operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '10')]).name
                    # ENTRADA PRODUCCION
                    elif sm.location_id.usage == 'production' and sm.location_dest_id.usage == 'internal':
                        serie = self.env['ir.sequence'].search([('code', '=', 'mrp.production'), (
                        'company_id', '=', str(sm.company_id.id))]).prefix or '0000'
                        x = len(serie)
                        correlativo = sm.production_id.name_seq
                        if correlativo == False:
                            correlativo = '0000'
                        else:
                            correlativo = correlativo[x:] or '0000'
                        tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                        operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '26')]).name
                    # DECONSTRUCCION
                    elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'internal' and unbuild_id != 0:
                        serie = self.env['ir.sequence'].search(
                            [('code', '=', 'mrp.unbuild'), ('company_id', '=', str(sm.company_id.id))]).prefix or '0000'
                        if serie == '0000':
                            correlativo = '0000'
                        else:
                            correlativo = sm.unbuild_id.name
                            x = len(serie)
                            correlativo = correlativo[x:]
                        tipo = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE10'), ('name', '=', '00')]).name
                        operacion = self.env['catalog.element'].search([('table_id.code', '=', 'PE.SUNAT.PLE_TABLE12'), ('name', '=', '26')]).name
                    # ADUANA
                    elif sm.location_id.usage == 'supplier' and sm.location_id.name == 'Aduana' and sm.location_dest_id.usage == 'internal':
                        serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                        correlativo = sm.picking_id.number_guia_supplier
                        if correlativo == False:
                            x = len(serie)
                            correlativo = sm.picking_id.name
                            correlativo = correlativo[x:]
                        tipo = sm.picking_id.tabla10.name or '00'
                        operacion = sm.picking_id.tabla12.name or '18'
                    # DEVOLUCION DE COMRA
                    elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'supplier' and sm.origin_returned_move_id != False:
                        serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                        correlativo = sm.picking_id.number_guia_supplier
                        if correlativo == False:
                            x = len(serie)
                            correlativo = sm.picking_id.name
                            correlativo = correlativo[x:]
                        else:
                            x = len(serie)
                            correlativo = correlativo[x:]
                        tipo = sm.picking_id.tabla10.name
                        operacion = sm.picking_id.tabla12.code
                    # DEVOLUCION DE VENTA
                    elif sm.location_id.usage == 'customer' and sm.location_dest_id.usage == 'internal' and sm.origin_returned_move_id != False:
                        # serie = sm.picking_id.serie_guia_supplier or sm.picking_id.picking_type_id.sequence_id.prefix
                        # correlativo = sm.picking_id.number_guia_supplier
                        if correlativo == False:
                            x = len(serie)
                            correlativo = sm.picking_id.name
                            correlativo = correlativo[x:]
                        else:
                            x = len(serie)
                            correlativo = correlativo[x:]
                        tipo = sm.picking_id.tabla10.name
                        operacion = sm.picking_id.tabla12.code
                    # ENTRADAS Y SALIDAS SIN FACTURAR
                    else:
                        # Transferencias Internas
                        if sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'internal':
                            # serie = sm.picking_id.l10n_latam_document_number.split('-')[0] or '-'
                            # correlativo = sm.picking_id.l10n_latam_document_number.split('-')[1]
                            if correlativo == False:
                                correlativo = 'SN'
                            else:
                                correlativo = sm.picking_id.l10n_latam_document_number.split('-', 1)
                        # Ventas sin facturar
                        elif sm.location_id.usage == 'internal' and sm.location_dest_id.usage == 'customer':
                            # serie = sm.picking_id.picking_type_id.sequence_guia_id.prefix  or '-'
                            # correlativo = sm.picking_id.l10n_latam_document_number.split('-', 1)
                            if correlativo == False:
                                # x=len(serie)
                                correlativo = sm.picking_id.name.split('-', 1)
                        # Compras sin facturar
                        elif sm.location_id.usage == 'supplier' and sm.location_dest_id.usage == 'internal':
                            # serie = sm.picking_id.serie_guia_supplier
                            # correlativo = sm.picking_id.number_guia_supplier
                            serie = "no factura"
                            correlativo = "--"
                        # Default
                        else:
                            serie = sm.picking_id.picking_type_id.sequence_id.prefix or '0000'
                            if serie == '0000':
                                correlativo = '0000'
                            else:
                                correlativo = sm.picking_id.name
                                x = len(serie)
                                correlativo = correlativo[x:] or '0000'

                        operacion = '00'  # or sm.picking_id.tabla12.code
                        tipo = '00'  # or sm.picking_id.tabla10.name

                # Validacion de UDM
                if medida == '--':
                    medida = product_id.uom_id.l10n_pe_edi_measure_unit_code

                # Busqueda de periodos
                ped_l = len(str(fecha.month))
                periodo = str(fecha.year) + '-' + str(fecha.month)
                if ped_l == 1:
                    periodo = str(fecha.year) + '-' + '0' + str(fecha.month)



                # Validacion de codigo de almacen
                if element.get('tipo_a') == 'entrada':
                    sl = self.env['stock.move'].search([('id', '=', str(move_id))]).location_dest_id.id
                    # almacen = self.env['stock.warehouse'].search([('lot_stock_id.id','=',str(sl))]).code_sunat
                    almacen = '0000'
                    if almacen == False:
                        # almacen = self.env['stock.warehouse'].search([('company_id.id','=',str(self.company_id.id)),('principal_warehouse','=',True)]).code_sunat
                        almacen = '0000'
                else:
                    sl = self.env['stock.move'].search([('id', '=', str(move_id))]).location_id.id
                    # almacen = self.env['stock.warehouse'].search([('lot_stock_id.id','=',str(sl))]).code_sunat
                    almacen = '0000'
                    if almacen == False:
                        # almacen = self.env['stock.warehouse'].search([('company_id.id','=',str(self.company_id.id)),('principal_warehouse','=',True)]).code_sunat
                        almacen = '0000'
                # slcad = self.env['stock.landed.cost'].search([('picking_ids','=',picking),('valuation_adjustment_lines.product_id.id','=',str(product_id.id))]).valuation_adjustment_lines

                costot = 0
                cantidadt = 0
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
                    campo7 = self.env['stock.move'].search([('id', '=', move_id)]).product_id.default_code or ''

                if element.get('tipo_a') == 'entrada':
                    price_e = element.get('price_unit')

                    if price_e == 0 and prom_price != 0:
                        price_e = prom_price
                    elif price_e == 0 and prom_price == 0:
                        price_e = price_used
                    # Validacion de USD a PEN
                    picking_purchase = self.env['stock.picking'].search([('name', '=', picking)]).origin or '-'

                    entrada = cantidad
                    total_cantidad = total_cantidad + cantidad
                    total_price = total_price + (entrada * price_e)
                    costo_total_entrada = (entrada * price_e) + costo_add
                    if cost_method == 'fifo':
                        rel_pro.append([entrada, price_e])

                    if total_cantidad > 0:
                        costo_final = (entrada * price_e) + costo_total
                        total_unit = round(costo_final / total_cantidad,2)
                        prom_price = total_unit
                    else:
                        total_unit = 0
                        costo_final = 0
                        prom_price = 0

                else:
                    price_s = prom_price
                    if cost_method == 'fifo':
                        price_s = 0
                        solictiado = cantidad
                        for elent in rel_pro:
                            if elent[0] <= solictiado and elent[0] != 0:
                                price_s += elent[0] * elent[1]
                                solictiado -= elent[0]
                                elent[0] = 0

                            if elent[0] > solictiado and elent[0] != 0:
                                price_s += solictiado * elent[1]
                                elent[0] = elent[0] - solictiado
                                break
                            if solictiado == 0:
                                break
                        price_s = price_s / cantidad

                    salida = cantidad
                    total_cantidad = total_cantidad - cantidad
                    total_price = total_price - (entrada * price_e)
                    costo_total_salida = (salida * price_s) + costo_add
                    if total_cantidad > 0:
                        costo_final = costo_total - (salida * price_s)
                        total_unit = costo_final / total_cantidad
                    else:
                        total_unit = 0
                        costo_final = 0
                        prom_price = 0

                if invoice_id:
                    line_inv = self.env['account.move.line'].search(
                        [('move_id', '=', invoice_id), ('product_id', '=', product_id.id)], limit=1)
                    invoice = line_inv.move_id
                    # serie, correlativo = self.get_series_correlative(line_inv)
                    # tipo = invoice.l10n_latam_document_type_id.code

                    if line_inv.move_id.state in ['cancel', 'anulled', 'draft']:
                        continue
                    if salida != 0:
                        # price_s = line_inv.price_subtotal/line_inv.quantity or 0.00
                        costo_total_salida = (salida * price_s) + costo_add
                    if entrada != 0:
                        price_e = line_inv.price_subtotal / line_inv.quantity or 0.00
                        costo_total_entrada = (entrada * price_e) + costo_add
                else:
                    sm = self.env['stock.move'].search([('id', '=', str(move_id))])
                    picking_id = sm.picking_id
                    if picking_id.sale_id:
                        sale_id = picking_id.sale_id
                        invoice_id = sale_id.mapped('invoice_ids')
                        if invoice_id:
                            if invoice_id.state in ['cancel', 'anulled', 'draft']:
                                continue
                            line_inv = self.env['account.move.line'].search(
                                [('move_id', 'in', invoice_id.ids), ('product_id', '=', product_id.id)], limit=1)
                            serie, correlativo = self.get_series_correlative(line_inv.move_id)
                            tipo = invoice_id.l10n_latam_document_type_id.code
                            if salida != 0:
                                if line_inv:
                                    # price_s = line_inv.price_subtotal/line_inv.quantity or 0.00
                                    costo_total_salida = (salida * price_s) + costo_add

                                    # serie = invoice_id.journal_id.invoice_sequence_id.prefix
                                    # correlativo = invoice_id.number.replace(serie,'')
                                    # tipo = invoice_id.l10n_latam_document_type_id.code
                                    operacion = invoice_id.journal_id.type_operation_table_12.code
                            # if entrada != 0:
                            #     price_e = line_inv.price_subtotal/line_inv.quantity or 0.00
                            #     costo_total_entrada = (entrada*price_e) + costo_add

                costo_total_salida = (salida * price_s) + costo_add

                if salida == 0:
                    salida = '0.00'
                else:
                    salida = round(salida, 2)

                if price_s == 0:
                    price_s = '0.00'
                else:
                    price_s = round(price_s, 2)

                if tipo_valuation == '2':
                    total_unit = '0.00'
                else:
                    round(total_unit, 2) or '0.00'

                costo_final = total_unit * total_cantidad

                costo_total = costo_final

                sheet.write(row, 0, fields.Date.to_string(fecha), normal)
                sheet.write(row, 1, tipo, normal)
                sheet.write(row, 2, serie, normal)
                sheet.write(row, 3, correlativo, normal)
                sheet.write(row, 4, operacion, normal)

                sheet.write(row, 5, entrada, normal)
                sheet.write(row, 6, price_e, normal)
                sheet.write(row, 7, costo_total_entrada, normal)

                sheet.write(row, 8, salida, normal)
                sheet.write(row, 9, price_s, normal)
                sheet.write(row, 10, costo_total_salida, normal)

                sheet.write(row, 11, total_cantidad, normal)
                sheet.write(row, 12, total_unit, normal)
                sheet.write(row, 13, costo_final, normal)
                row +=1




        return row


    def get_list_poermonth_by_date(self, date_from, date_to):
        list_date = []
        start_date = date_from
        end_date = date_to
        if date_to > date_from:
            while 1:
                if (start_date.month == end_date.month) and (start_date.year == end_date.year):
                    end_date_r = (end_date + relativedelta(days=1)) - relativedelta(seconds=1)
                    list_date.append([start_date,end_date_r])
                    break
                else:
                    first_date_month = datetime.date(start_date.year, start_date.month, 1)
                    last_date_month = (first_date_month + relativedelta(months=1)) - relativedelta(days=1)
                    last_date_month_r = (last_date_month + relativedelta(days=1)) - relativedelta(seconds=1)
                    list_date.append([start_date, last_date_month_r])
                    start_date = (first_date_month + relativedelta(months=1))

        return list_date



    def get_prduct_move_by_date(self, obj, odate_start, date_end):

        query = """ SELECT DISTINCT sm.product_id  product_id , pt.name
                    from stock_move sm
                    left join stock_picking sp on sm.picking_id = sp.id
                    left join product_product pp on pp.id = sm.product_id
                    left join product_template pt on pp.product_tmpl_id = pt.id
                    where sm.company_id = %s
                    and sp.scheduled_date BETWEEN '%s' AND '%s'
                    and sm.state = 'done'
                    and pt.type = 'product'
                    order by pt.name
        """ % (obj.company_id.id, odate_start, date_end)

        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        lit_pro = [result.get('product_id') for result in results]
        product = self.env['product.product'].browse(lit_pro)
        return product


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

