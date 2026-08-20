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

    @http.route(['/api/land/client/<string:vat>'], type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def get_client_land_vat(self, vat , **post):
        if not vat or   vat == '':
            return

        partner = request.env['res.partner'].sudo().search([('vat','=',vat)])

        if not partner:
            return

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

                lotes.append({
                    'id': sale.id ,
                    'contrato': sale.nro_internal_land ,
                    'mz': sale.mz_land ,
                    'lote': sale.lot_land ,

                })

        return {
            'success': True ,
            'name': partner.name ,
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
