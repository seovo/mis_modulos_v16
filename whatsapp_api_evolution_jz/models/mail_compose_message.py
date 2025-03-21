from odoo import api, fields, models
import requests
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"
    is_whatsapp_evolution_api = fields.Boolean(string="Enviar Whatsapp")
