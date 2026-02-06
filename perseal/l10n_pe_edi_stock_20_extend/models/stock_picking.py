# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import requests
import urllib.parse
from lxml import etree
from json.decoder import JSONDecodeError
from markupsafe import Markup
from datetime import datetime, timedelta
import pytz

from odoo import _, _lt, fields, models,api
import logging
_logger = logging.getLogger(__name__)

ERROR_MESSAGES = {
    "request": _lt("There was an error communicating with the SUNAT service.") + " " + _lt("Details:"),
    "json_decode": _lt("Could not decode the response received from SUNAT.") + " " + _lt("Details:"),
    "unzip": _lt("Could not decompress the ZIP file received from SUNAT."),
    "processing": _lt("The delivery guide is being processed by SUNAT. Click on 'Retry' to refresh the state."),
    "duplicate": _lt("A delivery guide with this number is already registered with SUNAT. Click on 'Retry' to try sending with a new number."),
    "response_code": _lt("SUNAT returned an error code.") + " " + _lt("Details:"),
    "response_unknown": _lt("Could not identify content in the response retrieved from SUNAT.") + " " + _lt("Details:"),
}
lima_timezone = pytz.timezone("America/Lima")


class Picking(models.Model):
    _inherit = "stock.picking"

    def _l10n_pe_edi_send_delivery_guide(self, edi_str, token):
        self.ensure_one()
        headers = {
            'Authorization': "Bearer " + token,
            'Content-Type': "Application/json",
        }
        edi_filename = "%s-09-%s" % (self.company_id.vat, self.l10n_latam_document_number)
        url = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/%s" % urllib.parse.quote_plus(edi_filename)

        edi_str = etree.tostring(etree.fromstring(edi_str), xml_declaration=True, encoding='ISO-8859-1')
        zip_file = self.env.ref('l10n_pe_edi.edi_pe_ubl_2_1')._l10n_pe_edi_zip_edi_document([('%s.xml' % edi_filename, edi_str)])
        data = {
            "archivo": {
                "nomArchivo": "%s.zip" % edi_filename,
                "arcGreZip": base64.b64encode(zip_file).decode(),
                "hashZip": hashlib.sha256(zip_file).hexdigest(),
            }
        }
        current_time = datetime.now(lima_timezone).strftime("%Y-%m-%d %H:%M:%S")
        try:
            _logger.info("Enviando guia de remision: '%s' a las '%s' desde '%s'", edi_filename, current_time, self.name)
            response = requests.post(url, json=data, headers=headers, verify=True, timeout=20)
            response.raise_for_status()
            _logger.info("Respuesta de la guia '%s' : '%s'", edi_filename, response.text)
        except requests.exceptions.RequestException as e:
            _logger.error("Error al enviar la guia '%s' de remisión: '%s'", edi_filename, e)
            to_return = {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["request"], e))}
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                to_return.update({"error_reason": "unauthorized"})
            return to_return
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["json_decode"], e))}

        if isinstance(response_json.get("errors"), list) and len(response_json["errors"]) > 0 and isinstance(response_json["errors"][0], dict):
            code = response_json["errors"][0].get("cod", "")
            msg = response_json["errors"][0].get("msg", "")
            return {"error": str(Markup("%s<br/>%s: %s") % (ERROR_MESSAGES["response_code"], code, msg))}
        if not response_json.get("numTicket"):
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["response_unknown"], response_json))}

        return {"ticket_number": response_json["numTicket"]}

    def button_validate(self):
        l10n_pe_edi_departure_start_date = self.l10n_pe_edi_departure_start_date
        picking = super().button_validate()
        self.l10n_pe_edi_departure_start_date = l10n_pe_edi_departure_start_date
        return picking

