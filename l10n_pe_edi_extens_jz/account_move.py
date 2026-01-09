from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import requests
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_date','l10n_latam_document_type_id.code')
    def change_date_jz_jz(self):
        for record in self:
            if record.invoice_date and record.state == 'draft' :
                diff = fields.Datetime.now().date() - record.invoice_date


                #para facturas

                day_min = 5

                if record.l10n_latam_document_type_id.code == '01':
                    day_min = 3


                if diff.days > day_min :
                    raise ValidationError(f'SOLO SE PERMITE COLOCAR FECHAS HASTA {day_min} DIAS ATRAS')



    def action_post(self):
        self.change_date_jz_jz()
        res = super().action_post()
        if len(self) == 1 :
            if self.edi_document_ids:
                self.button_process_edi_web_services()
        return res






    def action_retry_edi_documents_error(self):

        #self.validate_cpe()

        if len(self) == 1:
            if self.state == 'to_send':
                record.button_draft()
                return
                # record.action_post()





        res = super(AccountMove, self).action_retry_edi_documents_error()
        return res
    #    for record in self:
    #        record.edi_document_ids.unlink()
    #        record.button_process_edi_web_services()



    def validate_cpe(self):
        for record in self:
            if record.edi_state == 'to_send':
               # URL del formulario
               url = "https://ww1.sunat.gob.pe/ol-ti-itconsultaunificadalibre/consultaUnificadaLibre/consultaIndividual"

               name = record.name.replace(' ','')
               split_name = name.split('-')
               fecha_formateada = record.invoice_date.strftime("%d/%m/%Y")

               # Datos a enviar en formato form-data
               data = {
                   "numRuc": record.company_id.vat ,  # RUC del emisor
                   "codComp": record.l10n_latam_document_type_id.code ,          # Código del comprobante
                   "numeroSerie": split_name[0] ,    # Número de serie
                   "numero": split_name[1] ,      # Número del comprobante
                   "codDocRecep": record.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code  ,       # Código del documento del receptor
                   "numDocRecep": record.partner_id.vat , # Número del documento del receptor
                   "fechaEmision": fecha_formateada , # Fecha de emisión
                   "monto": record.amount_total ,        # Importe total
                   "token": "zty5wf3e1alzc1le1ee8cpg5jnnazqj55w7bv5du8p6681pby0jw"  # Token
               }

               # Realizar la solicitud POST
               response = requests.post(url, data=data)
               # Verificar la respuesta
               if response.status_code == 200:
                   #print("Solicitud exitosa.")
                   data = response.json()

                   objeto_json = json.loads(data)

                   estado_cp = objeto_json['data']['estadoCp']

                   if estado_cp == '1':
                       for edi in record.edi_document_ids:
                           edi.state = 'sent'
                           edi.blocking_level = False



                   #raise ValueError([data,objeto_json,estado_cp])


               else:
                   print(f"Error en la solicitud: {response.status_code}")



    def button_process_edi_web_services(self):



        if len(self) == 1:
            note = self.narration
            self.narration = None


        res = super().button_process_edi_web_services()

        #if self.l10n_pe_edi_operation_type == '1001':
        if len(self) == 1:
            self.narration = note



        return  res
