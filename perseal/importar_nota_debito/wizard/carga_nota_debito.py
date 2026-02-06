# -*- coding: utf-8 -*-

import base64
import xlrd

from odoo import api, fields, models
from odoo.exceptions import UserError


class CargaNotaDebito(models.TransientModel):
    _name = "carga.nota.debito"
    _description = "Carga de nota de débito"

    archivo = fields.Binary(string="Archivo (*.xlsx)")
    nombre_archivo = fields.Char(string="Nombre del archivo")

    def cargar_archivo(self):
        decoded_data = base64.decodebytes(self.archivo)
        wb = xlrd.open_workbook(file_contents=decoded_data)
        worksheet = wb.sheet_by_index(0)

        for fila in range(1, worksheet.nrows):
            move = worksheet.cell(fila, 0).value
            if not move:
                raise UserError('El número del documento origen es obligatorio, fila {0} del archivo excel.'.format(fila))
            move_id = self.env['account.move'].search([
                ('name', '=', move),
                ('company_id', '=', self.env.company.id),
            ])
            if not move_id:
                raise UserError('No se encontró el documento origen {0} en la base de datos, fila {1} del archivo excel.'.format(move, fila))

            name = worksheet.cell(fila, 1).value
            # if not name:
            #     raise UserError('El número de la nota de débito es obligatorio, fila {0} del archivo excel.'.format(fila))

            fecha = worksheet.cell(fila, 2).value
            if not fecha:
                raise UserError('La fecha de la nota de débito es obligatoria, fila {0} del archivo excel.'.format(fila))
            date = xlrd.xldate.xldate_as_datetime(fecha, wb.datemode).date()

            journal = worksheet.cell(fila, 3).value
            if not journal:
                raise UserError('El diario de la nota de débito es obligatorio, fila {0} del archivo excel.'.format(fila))
            journal_id = self.env['account.journal'].sudo().search([
                ('name', '=', journal),
                ('company_id', '=', self.env.company.id),
            ])
            if not journal_id:
                raise UserError('No se encontró el diario {0} en la base de datos, fila {1} del archivo excel.'.format(journal, fila))

            ref = worksheet.cell(fila, 4).value
            razon = worksheet.cell(fila, 5).value
            cod_razon = False
            if not razon:
                raise UserError('La razón del débito es obligatorio, fila {0} del archivo excel.'.format(fila))
            if razon == 'Intereses por mora':
                cod_razon = '01'
            elif razon == 'Aumento en el valor':
                cod_razon = '02'
            elif razon == 'Penalidades/ otros conceptos':
                cod_razon = '03'
            elif razon == 'Ajustes de operaciones de exportación':
                cod_razon = '11'
            elif razon == 'Ajustes afectos al IVAP':
                cod_razon = '12'
            if not cod_razon:
                raise UserError('La razón del débito no es válida, fila {0} del archivo excel.'.format(fila))

            document_type_id = self.env['l10n_latam.document.type'].sudo().search([
                ('code', '=', '08'),
                ('doc_code_prefix', '=', journal_id.code[0:1])
            ])
            if not document_type_id:
                raise UserError(
                    'No se encontró el tipo de documento Nota de débito en la base de datos.  Por favor comunicarse con el administrador del sistema.')

            producto = worksheet.cell(fila, 6).value
            if not producto:
                raise UserError('El producto es obligatorio, fila {0} del archivo excel.'.format(fila))
            product_id = self.env['product.product'].search([
                ('name', '=', producto),
            ])
            if not product_id:
                raise UserError(
                    'No se encontró el producto {0} en la base de datos, fila {1} del archivo excel.'.format(producto,
                                                                                                             fila))
            cantidad = worksheet.cell(fila, 8).value
            if not cantidad:
                raise UserError('La cantidad es obligatoria, fila {0} del archivo excel.'.format(fila))

            precio_unitario = worksheet.cell(fila, 9).value
            if not precio_unitario:
                raise UserError('El precio unitario es obligatorio, fila {0} del archivo excel.'.format(fila))

            cuenta_analitica = worksheet.cell(fila, 7).value
            analytic_account_id = False
            if cuenta_analitica:
                analytic_account_id = self.env['account.analytic.account'].search([
                    ('name', '=', cuenta_analitica),
                ])

            values = {
                'name': name if name else '/',
                # 'l10n_latam_document_number': name if name else False,
                'partner_id': move_id.partner_id.id,
                'partner_shipping_id': move_id.partner_shipping_id.id,
                'date': date,
                'invoice_date': date,
                'journal_id': journal_id.id,
                'ref': ref,
                'payment_reference': ref,
                'debit_origin_id': move_id.id,
                'move_type': 'out_invoice',
                'l10n_pe_edi_charge_reason': cod_razon,
                'l10n_latam_document_type_id': document_type_id.id,
                'invoice_origin': move_id.name,
                'invoice_line_ids': [(0, 0, {
                    'name': product_id.name,
                    'product_id': product_id.id,
                    'product_uom_id': product_id.uom_id.id,
                    'quantity': cantidad,
                    'price_unit': precio_unitario,
                    'analytic_distribution': {str(analytic_account_id.id): 100.0},
                    'tax_ids': [(6, 0, product_id.taxes_id.ids)],
                })],
            }

            # existe_move_id = self.env['account.move'].search([
            #     ('name', '=', name),
            #     ('company_id', '=', self.env.company.id),
            #     ('move_type', '=', 'out_invoice'),
            # ])
            # if existe_move_id:
            #     if existe_move_id.state == 'draft':
            #         existe_move_id.line_ids.unlink()
            #         existe_move_id.write(values)
            # else:
            new_move = self.env['account.move'].create(values)
            new_move._compute_name()
            move_msg = "Esta nota de débito se creó desde: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>" % (move_id.id, move_id.name)
            new_move.message_post(body=move_msg)
