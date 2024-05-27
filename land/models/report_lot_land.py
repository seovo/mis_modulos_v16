from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date
'''
class ReportLotLand(models.Model):
    _name        = 'report.lot.land'
    _description = 'report.lot.land'
    mz_value_id     = fields.Many2one('product.attribute.value',string="Manzana")
    #stage_value_id  = fields.Many2one('product.template.attribute.value')
    max_lot         = fields.Integer(string='Cantidad Lotes')
    line_ids        = fields.One2many('report.lot.land.line','report_lot_land_id')
    product_tmp_id  = fields.Many2one('product.template',string='Producto')

    _sql_constraints = [
        (
            "unique_report_lot_land",
            "unique(product_tmp_id, mz_value_id )",
            "There can be no duplication mz and stage",
        )
    ]
    
'''

class ReportLotLandLine(models.Model):
    _name        = 'report.lot.land.line'
    _description = 'report.lot.land.line'
    #report_lot_land_id = fields.Many2one('report.lot.land')
    mz_value_id        = fields.Many2one('product.template.attribute.value', string="Manzana")
    name               = fields.Char()
    shape              = fields.Selection([('regular','Regular'),('irregular','Irregular')],string='Forma')
    area               = fields.Float()
    front              = fields.Float(string='Frente')
    large1             = fields.Float(string='Largo 1')
    large2             = fields.Float(string='Largo 2')
    background         = fields.Float(string='Fondo')
    price              = fields.Float(string='Precio')
    order_ids          = fields.One2many('sale.order','report_lot_land_line_id')
    product_tmp_id = fields.Many2one('product.template', string='Producto')

    _sql_constraints = [
        (
            "unique_report_lot_land_line",
            "unique(report_lot_land_id, number_lot )",
            "There can be no report.lot.land.line",
        )
    ]

