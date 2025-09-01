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

class Binary(http.Controller):
    @http.route('/web/binary/download_excell_report_schedule_land/<model("res.company"):company>', type='http', auth="public")
    #@serialize_exception
    def download_excell_report_schedule_land(self, company , **kw):
        excel_data = request.env['report.schedule.land'].get_report_xls(company)

        filename = f'Report_Cuotas_{company.name}.xlsx'
        filecontent = base64.b64decode(excel_data or '')
        return request.make_response(filecontent, [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', content_disposition(filename))
        ])

    @http.route('/web/binary/download_excell_report_schedule_land_order/<model("sale.order"):sale>', type='http', auth="public")
    #@serialize_exception
    def download_excell_report_schedule_land_sale(self, sale , **kw):
        excel_data = request.env['report.schedule.land'].get_report_xls(None,sale=sale)

        filename = f'Report_Cuotas_{sale.partner_id.name}_{sale.nro_internal_land}.xlsx'
        filecontent = base64.b64decode(excel_data or '')
        return request.make_response(filecontent, [
            ('Content-Type', 'application/vnd.ms-excel'),
            ('Content-Disposition', content_disposition(filename))
        ])
