# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from requests.exceptions import ConnectionError as ReqConnectionError, HTTPError, InvalidSchema, InvalidURL, ReadTimeout

from odoo import models, api, _, _lt
from zeep.transports import Transport
from lxml import etree
from lxml import objectify
from zeep import Client, Settings
from zeep.exceptions import Fault

import logging

_logger = logging.getLogger( __name__ )


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_pe_edi_post_invoice_web_service(self, invoice, edi_filename, edi_str):
        self.xml_log(invoice, edi_filename, edi_str)
        provider = invoice.company_id.l10n_pe_edi_provider
        res = getattr(self, '_l10n_pe_edi_sign_invoices_%s' % provider)(invoice, edi_filename, edi_str)

        if res.get('error'):
            return res

        # Chatter.
        documents = []
        if res.get('xml_document'):
            documents.append(('%s.xml' % edi_filename, res['xml_document']))
        if res.get('cdr'):
            documents.append(('CDR-%s.xml' % edi_filename, res['cdr']))
        if documents:
            zip_edi_str = self._l10n_pe_edi_zip_edi_document(documents)
            res['attachment'] = self.env['ir.attachment'].create({
                'res_model': invoice._name,
                'res_id': invoice.id,
                'type': 'binary',
                'name': '%s.zip' % edi_filename,
                'datas': base64.encodebytes(zip_edi_str),
                'mimetype': 'application/zip',
            })
            message = _("The EDI document was successfully created and signed by the government.")
            invoice.with_context(no_new_invoice=True).message_post(
                body=message,
                attachment_ids=res['attachment'].ids,
            )
        return res

    def xml_log(self,invoice, edi_filename, edi_str):
        edi_tree = objectify.fromstring(edi_str)
        edi_str = etree.tostring(edi_tree, xml_declaration=True, encoding='ISO-8859-1')
        zip_edi_str = self._l10n_pe_edi_zip_edi_document([('%s.xml' % edi_filename, edi_str)])
        res = self.env['ir.attachment'].create({
            'res_model': invoice._name,
            'res_id': invoice.id,
            'type': 'binary',
            'name': '%s-XML.zip' % edi_filename,
            'datas': base64.encodebytes(zip_edi_str),
            'mimetype': 'application/zip',
        })
        message = _("The EDI document was successfully created and signed by the government.")
        invoice.with_context(no_new_invoice=True).message_post(
            body=message,
            attachment_ids=res.ids,
        )