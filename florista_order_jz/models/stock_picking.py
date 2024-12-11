from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    sched_date = fields.Date(compute='get_sche_date',store=True)
    until_hour_florista = fields.Many2one('until.hour.florista', string="Entregar Hasta")
    product_ids = fields.Many2many('product.product',compute='get_products_florista')

    @api.depends('scheduled_date')
    def get_sche_date(self):
        for record in self:
            record.sched_date = (record.scheduled_date - timedelta(hours=5)).date()

    @api.depends('move_ids_without_package')
    def get_products_florista(self):
        for line in self:
            ids = []
            for move in line.move_ids_without_package:
                if move.product_id:
                    ids.append(move.product_id.id)
            line.product_ids = [(6,0,ids)] if ids else None
