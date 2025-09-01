from odoo import api, fields, models
import io
try:
    import base64
except:
    install('base64')

try:
    import xlsxwriter
except:
    install('xlsxwriter')

class ReportScheduleLand(models.TransientModel):
    _name = "report.schedule.land"
    _description  = "report.schedule.land"
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def do_excell(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/binary/download_excell_report_schedule_land/{self.company_id.id}',
            'target': 'self',
        }

    def get_report_xls(self):
        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        sheet = workbook.add_worksheet()
        self.get_report_xls_data(workbook, sheet)
        workbook.close()
        excel_file = base64.encodebytes(fp.getvalue())
        fp.close()
        return excel_file

    def get_report_xls_data(self,workbook, sheet):
        bold = workbook.add_format({'bold': True})
        sheet.write(xc, 1, 'A', bold)
        sheet.write(xc, 2, 'B', bold)
        #sheet.write(xc, 3, 'UM', bold)
        #sheet.write(xc, 4, _('Unit Cost'), bold)
        #sheet.write(xc, 5, _('Total Cost'), bold)
        #sheet.write(xc, 6, _('Price Unit'), bold)
        #sheet.write(xc, 7, _('Price Total'), bold)


