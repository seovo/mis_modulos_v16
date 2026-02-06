from odoo import _, _lt, fields, models
import base64
from lxml import etree
from lxml import objectify
import logging

_logger = logging.getLogger( __name__ )


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _l10n_pe_edi_send_delivery_guide(self, edi_filename, edi_str, token):
        self.xml_log(edi_filename, edi_str)
        res = super(Picking, self)._l10n_pe_edi_send_delivery_guide(edi_filename, edi_str, token)
        return res

    def xml_log(self, edi_filename, edi_str):
        edi_tree = objectify.fromstring(edi_str)
        edi_str = etree.tostring(edi_tree, xml_declaration=True, encoding='ISO-8859-1')
        zip_edi_str = self._l10n_pe_edi_zip(edi_str, edi_filename)
        self.env['ir.attachment'].create({
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'name': '%s-TEST_XML.zip' % edi_filename,
            'datas': base64.encodebytes(zip_edi_str),
            'mimetype': 'application/zip',
        })
        # message = _("The EDI document was successfully created and signed by the government.")
        # self.with_context(no_new_invoice=True).message_post(
        #     body=message,
        #     attachment_ids=res.ids,
        # )