from odoo import http
from odoo.http import request
#from odoo.addons.web.controllers.main import serialize_exception, content_disposition
#from odoo.addons.web.controllers.main import  content_disposition
#from odoo.http import content_disposition, Controller, request, route
from odoo.http import content_disposition
import io
try:
    import base64
except:
    install('base64')

try:
    import xlsxwriter
except:
    install('xlsxwriter')

import datetime

class Controller(http.Controller):

    @http.route(
        ['/ui/land'],
        type="http",
        auth="public",
        methods=["POST", "GET"],
        website=True,
        csrf=True,
    )
    def form_adjunto(self,  **post):

        data = {}

        return http.request.render("land.index_form_adjunto", data)

    @http.route(['/api/up/land'], type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def upload_land(self, **post):
        # Recepcionar el adjunto en una variable (solo por ahora)
        adjunto = request.httprequest.files.get('adjunto')

        # Capturar los lotes seleccionados (checkboxes con name="lotes")
        lotes_seleccionados = request.httprequest.form.getlist('lotes')
        company = None

        sale_ids = []

        for lote_id in lotes_seleccionados:
            sale = request.env['sale.order'].sudo().search([('id','=',int(lote_id))])
            if not company:
                company = sale.company_id
            if company:
                if company != sale.company_id:
                    raise ValueError('NO PUEDE SELEECIONAR LOTES DE DIFERENTES PROYECTOS')

            sale_ids.append(sale.id)


        wizard = request.env['sale.advance.payment.inv'].sudo().create({
            'advance_payment_method': 'delivered',
            'sale_order_ids': [(6,0,sale_ids)]
        })

        #sales = request.env['sale.order'].sudo().search([('id','in',sale_ids)])
        wizard._check_amount_is_positive()
        invoice = wizard._create_invoices(wizard.sale_order_ids)



        # TODO: cuando lo indiques, guardar el adjunto en el chatter de una factura

        if adjunto and invoice:

            attachment = request.env['ir.attachment'].sudo().create({
                   'name': adjunto.filename,
                   'datas': base64.b64encode(adjunto.read()),
                   'type': 'binary',
            })

            invoice.message_post(
                   body='Comprobante adjunto',
                   attachment_ids=[attachment.id],
            )

        return request.redirect('/ui/land')

    @http.route(['/api/land/client/<string:vat>'], type='json', auth='public', methods=['POST'],
                website=True, csrf=False)
    def get_client_land_vat(self, vat , **post):
        if not vat or   vat == '':
            return

        partner = request.env['res.partner'].sudo().search([('vat','=',vat)])

        if not partner:
            return {
                'success': True,
                'name': '',
                'type_identification': None,
                'email': '',
                'phone': ''
            }

        if len(partner) > 1 :
            return {
                'error': 'Mas de un registro encontrado'
            }

        lotes = []

        if partner.sale_order_ids:
            for sale in partner.sale_order_ids:

                if sale.state !=  'sale':
                    continue

                if sale.stage_land ==  'cancel':
                    continue

                try:
                    name_company = sale.company_id.partner_id.category_id.name
                except:
                    name_company = ''

                lotes.append({
                    'id': sale.id ,
                    'contrato': f'''CN {sale.nro_internal_land} {name_company}''' ,
                    'mz': sale.mz_land ,
                    'lote': sale.lot_land ,
                    'company': sale.company_id.id

                })

        return {
            'success': True ,
            'name': partner.name ,
            'type_identification': partner.l10n_latam_identification_type_id.l10n_pe_vat_code ,
            'email': partner.email ,
            'phone': partner.phone or partner.mobile ,
            'lotes': lotes
        }



    @http.route('/web/binary/download_excell_report_schedule_land/<model("res.company"):company>', type='http', auth="public")
    #@serialize_exception
    def download_excell_report_schedule_land(self, company , **kw):
        #raise ValueError(kw)

        excel_data = request.env['report.schedule.land'].get_report_xls(company,kw=kw)

        filename = f'REPORTE_CUOTAS_{company.name}.xlsx'

        if 'byear' in kw:
            if kw['byear'] and str(kw['byear']) != 'False' :
                filename = f'''Balance_Anual_{kw.get('year')}_{company.name}.xlsx'''


        filecontent = base64.b64decode(excel_data or '')
        return request.make_response(filecontent, [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', content_disposition(filename))
        ])

    @http.route('/web/binary/download_excell_report_schedule_land_order/<model("sale.order"):sale>', type='http', auth="public")
    #@serialize_exception
    def download_excell_report_schedule_land_sale(self, sale , **kw):

        excel_data = request.env['report.schedule.land'].get_report_xls(None,sale=sale,kw=kw)

        filename = f'REPORTE_CUOTAS_{sale.partner_id.name}_{sale.nro_internal_land}.xlsx'
        filecontent = base64.b64decode(excel_data or '')
        return request.make_response(filecontent, [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', content_disposition(filename))
        ])
