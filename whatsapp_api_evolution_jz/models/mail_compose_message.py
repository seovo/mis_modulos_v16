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
    number_whatsapp_evolution_api = fields.Char(string='Enviar a')

    @api.onchange('res_ids','is_whatsapp_evolution_api')
    def change_res_ids(self):
        array = ast.literal_eval(self.res_ids)

        objects = self.env[self.model].search([('id', 'in', array)])



        for object in objects:
            try:
                phone = object.partner_id.phone or object.partner_id.mobile
            except:
                continue

            if not phone:
                continue
            phone = phone.replace('+', '')
            phone = phone.replace(' ', '')

            self.number_whatsapp_evolution_api = phone

            if self.model in ['sale.order'] and self.is_whatsapp_evolution_api:
                url_main =  self.env['ir.config_parameter'].search([('key','=','web.base.url')])
                url = object.action_preview_sale_order()['url']
                self.text_whatsapp_evolution_api = f'''  revise la orden aqui: {url_main.value}{url}  '''



    def action_send_mail(self):

        #raise ValueError(self.res_ids)

        #raise ValueError(self.message_type)


        responses = []

        if self.is_whatsapp_evolution_api and self.message_type == 'comment' :

            token = self.env.company.token_whatsapp_evolution_api

            phone = self.number_whatsapp_evolution_api

            if not phone:
                raise ValidationError('No se indico Telefono')

            # raise ValueError(phone)

            # if len(phone) != 11 :
            #    raise ValidationError(f'No tiene los digitos suficientes {phone}')

            if not self.text_whatsapp_evolution_api:
                raise ValidationError('No se indico el mensaje')

            msg = f'''{self.subject} , {self.text_whatsapp_evolution_api}'''

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }

            dominio = self.env.company.url_whatsapp_evolution_api

            url = f'{dominio}/api/message/send-text'
            data = {
                "number": phone,
                "message": msg
            }

            if self.attachment_ids:
                import base64
                if len(self.attachment_ids) != 1:
                    raise ValidationError('Solo se puede enviar un archivo')

                datas = str(self.attachment_ids.datas)

                # Decodificar de base64 a bytes
                # contenido_decodificado = base64.b64decode(datas)
                # Si necesitas convertirlo a una cadena de texto
                # datas = contenido_decodificado.decode('utf-8', errors='ignore')

                # Quitar el prefijo 'b' y la comilla final
                datas = datas[2:-1]

                # raise ValueError(self.attachment_ids.mimetype)

                '''
                                        data = {
                    "media": "image", // media | video | audio
                    "caption": "Plain Text message",
                    "link": "https://....", // url | base64
                    "number": "51123456789"
                }


                                        '''

                if self.attachment_ids.mimetype == 'application/pdf':
                    url = f'{dominio}/api/message/send/pdf'
                elif 'image/' in self.attachment_ids.mimetype:
                    raise ValidationError('Solo se permiten PDFS')
                    url = f'{dominio}/api/message/send-media'
                    data.update({
                        'media': 'image',
                        'caption': msg,
                        'link': datas
                    })
                # else:
                #    raise ValueError(self.attachment_ids.mimetype)

                # raise ValidationError([self.attachment_ids.display_name, url , datas])

                data.update({
                    'file': datas,
                    'filename': self.attachment_ids.display_name
                })

            res = requests.post(url, json=data, headers=headers)

            try:
                response = res.json()
            except:
                raise ValueError([res, data])

            json_response = json.dumps(response, indent=4)

            responses.append(str(json_response))


        if responses:
            self.body = str(responses)

        res = super().action_send_mail()



        return res
