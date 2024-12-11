from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    sched_date = fields.Date(compute='get_sche_date',store=True)
    until_hour_florista = fields.Many2one('until.hour.florista', string="Entregar Hasta")

    @api.depends('scheduled_date')
    def get_sche_date(self):
        for record in self:
            record.sched_date = (record.scheduled_date - timedelta(hours=5)).date()