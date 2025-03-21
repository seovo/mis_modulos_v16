from odoo import api, fields, models
import requests
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"
    is_whatsapp_evolution_api = fields.Boolean(string="Enviar Whatsapp")

    def action_send_mail(self):
        res = super().action_send_mail()

        if self.is_whatsapp_evolution_api:
            token = '2Qrlw2jjp30P7CGFlcSo1FkJ5SX27X'
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json" ,
                "Authorization": f"Bearer {token}",
            }
            url = 'https://xalachi.qr.xalachi.com/api/message/send-text'
            data = {
                #"number": "123456789",
                "number": "50664307914",
                "message": "Plain text message"
            }
            res = requests.post(url, json=data, headers=headers)

            raise ValueError(res.json())

        return res
