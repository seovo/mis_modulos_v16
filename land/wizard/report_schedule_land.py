from odoo import api, fields, models

class ReportScheduleLand(models.TransientModel):
    _name = "report.schedule.land"
    _description  = "report.schedule.land"
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def do_excell(self):
        return
