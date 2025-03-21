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

                #raise ValueError(phone)

                #if len(phone) != 11 :
                #    raise ValidationError(f'No tiene los digitos suficientes {phone}')

                if not self.text_whatsapp_evolution_api:
                    raise ValidationError('No se indico el mensaje')

                msg = f'''{self.subject} , {self.text_whatsapp_evolution_api}'''


                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }

                dominio = 'https://xalachi.qr.xalachi.com'

                url = f'{dominio}/api/message/send-text'
                data = {
                    # "number": "123456789",
                    "number": phone,
                    "message": msg
                }


                if self.attachment_ids:
                    import base64
                    if len(self.attachment_ids) != 1:
                        raise ValidationError('Solo se puede enviar un archivo')

                    datas = str(self.attachment_ids.datas)

                    # Decodificar de base64 a bytes
                    #contenido_decodificado = base64.b64decode(datas)
                    # Si necesitas convertirlo a una cadena de texto
                    #datas = contenido_decodificado.decode('utf-8', errors='ignore')

                    # Quitar el prefijo 'b' y la comilla final
                    datas = datas[2:-1]


                    #raise ValueError(self.attachment_ids.mimetype)

                    if self.attachment_ids.mimetype == 'application/pdf':
                        url = f'{dominio}/api/message/send/pdf'
                    else:
                        url = f'{dominio}/api/message/send-media'

                    raise ValidationError([self.attachment_ids.display_name, url , datas])



                    data.update({
                         'file': datas ,
                         'filename': self.attachment_ids.display_name
                    })


                res = requests.post(url, json=data, headers=headers)


                try:
                    response = res.json()
                except:
                    raise ValueError([res,data])

                json_response = json.dumps(response, indent=4)

                responses.append(str(json_response))

        if responses:
            self.body = str(responses)

        res = super().action_send_mail()



        return res
