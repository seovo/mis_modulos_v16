# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from odoo.tools.safe_eval import safe_eval
import qrcode
import base64
import io
import re


class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_number = fields.Char(related='account_move.name')
    client_document_type = fields.Char(related='partner_id.l10n_latam_identification_type_id.name', string='Document Type')
    order_document_type = fields.Char(related='account_move.l10n_latam_document_type_id.name', string='Payment Type')
    qr_code_image = fields.Binary()


    # Función para retornar los datos extras que no se cargan por defecto en el POS
    # Para mostrarlos en la personalización del ticket de venta
    @api.model
    def get_extra_report_data(self, order_name):
        order = self.search([('pos_reference', '=', order_name)], limit=1)
        data_to_print = {
                'invoice_number': order.invoice_number,
                'order_payment_type': order.order_payment_type,
                'client_document_type': order.client_document_type,
                'country': order.partner_id.country_id.name,
                'state': order.partner_id.state_id.name,
                'city': order.partner_id.city_id.name,
                'l10n_pe_district': order.partner_id.l10n_pe_district.name,
                'street': order.partner_id.street,
                'street2': order.partner_id.street2,
                'zip': order.partner_id.zip,
                }
        data_to_print.update(self._l10n_pe_edi_custom_qr_values(order.account_move, order.amount_tax))
        return data_to_print


    def _l10n_pe_edi_get_serie_folio_custom(self, name):
        number_match = [rn for rn in re.finditer(r'\d+', name.replace(' ', ''))]
        serie = name[:number_match[-1].start()].replace('-', '').replace(' ', '') or None
        folio = number_match[-1].group() or None
        return {'serie': serie, 'folio': folio}



    # Función para generar el código QR con el mismo formato que se genera por defecto en Odoo para Perú
    # Pero omitiendo los datos que no se encuentren disponibles a la hora de visualizar el ticket de venta
    # Debido a que el envío a SUNAT puede ser demorado.
    def _l10n_pe_edi_custom_qr_values(self, invoice, amount_tax):
        igv_tax_amount = str(amount_tax)

        serie_folio = self._l10n_pe_edi_get_serie_folio_custom(invoice.name)
        qr_code_values = [
            invoice.company_id.vat,
            invoice.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            serie_folio['serie'],
            serie_folio['folio'],
            igv_tax_amount,
            str(invoice.amount_total),
            fields.Date.to_string(invoice.date),
            invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            invoice.commercial_partner_id.vat or '00000000',
        ]

        aux = {'qr_str': '|'.join(qr_code_values) + '|\r\n',}

        img = qrcode.make(aux.get('qr_str'))
        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        img_bytes = result.read()
        base64_encoded_result_bytes = base64.b64encode(img_bytes)
        base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
        return {'qr_code_text': base64_encoded_result_str}

