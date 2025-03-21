from odoo import api, fields, models
import requests
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests
import ast
import json

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"
    is_whatsapp_evolution_api = fields.Boolean(string="Enviar Whatsapp")
    text_whatsapp_evolution_api = fields.Text(string='Texto Whatsapp')

    def action_send_mail(self):

        #raise ValueError(self.res_ids)

        array = ast.literal_eval(self.res_ids)

        objects = self.env[self.model].search([('id','in',array)])

        responses = []

        for object in objects:
            if self.is_whatsapp_evolution_api:
                token = '2Qrlw2jjp30P7CGFlcSo1FkJ5SX27X'

                phone = object.partner_id.phone or object.partner_id.mobile

                if not phone:
                    raise ValidationError('No se indico Telefono')

                phone = phone.replace('+','')
                phone = phone.replace(' ','')

                raise ValueError(phone)

                if len(phone) != 11 :
                    raise ValidationError(f'No tiene los digitos suficientes {phone}')




                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                url = 'https://xalachi.qr.xalachi.com/api/message/send-text'
                data = {
                    # "number": "123456789",
                    "number": "50664307914",
                    "message": "Plain text message"
                }
                res = requests.post(url, json=data, headers=headers)

                response = res.json()

                json_response = json.dumps(response, indent=4)

                responses.append(str(json_response))

        if responses:
            self.body = str(responses)

        res = super().action_send_mail()



        return res
