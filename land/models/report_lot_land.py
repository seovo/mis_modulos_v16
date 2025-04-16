from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date

class LandZona(models.Model):
    _name        = 'land.zona'
    _description = 'land.zona'
    name  = fields.Char(required=True)
    value = fields.Float()

    

class ReportLotLandLine(models.Model):
    _name        = 'report.lot.land.line'
    _description = 'report.lot.land.line'
    mz_value_id        = fields.Many2one('product.template.attribute.value', string="Manzana ID")

    manzana            = fields.Char()
    name               = fields.Char(string="Lote")
    area               = fields.Float()
    zona               = fields.Many2one('land.zona')
    ettapa              = fields.Char(string="Etapa")

    shape              = fields.Selection([('regular','Regular'),('irregular','Irregular')],string='Forma')


    front              = fields.Float(string='Frente')
    large1             = fields.Float(string='Largo 1')
    large2             = fields.Float(string='Largo 2')
    background         = fields.Float(string='Fondo')
    price              = fields.Float(string='Precio',compute='set_price')
    order_ids          = fields.One2many('sale.order','report_lot_land_line_id',string="Ventas")
    move_ids           = fields.One2many('account.move','report_lot_land_line_id',string="Separaciones")
    product_tmp_id     = fields.Many2one('product.template', string='Producto',required=True)
    state              = fields.Selection([('sale','Vendido'),('free','Libre'),('reserved','Separado')],
                                           compute='get_state',store=True,string="Estado")

    @api.depends('manzana')
    def _compute_display_name(self):
        for record in self:
            name = record.name
            if record.manzana:
                name = f'{name} - {record.manzana}'
            record.display_name = name

    @api.depends('zona','area')
    def set_price(self):
        for record in self:
            record.price = record.zona.value * record.area if record.zona and record.area else 0

    @api.depends('order_ids','move_ids')
    def get_state(self):
        for record in self:
            state = 'free'

            for move in record.move_ids:
                if move.state in ['posted']:
                    state = 'reserved'

            for order in record.order_ids:
                if order.state in ['done','sale']:
                    if order.stage_land == 'signed':
                        state = 'sale'
                    if not order.stage_land :
                        if order.invoice_ids:
                            all_initial = True
                            for invoice in order.invoice_ids:
                                if not invoice.is_initial_land:
                                    all_initial = False
                            if all_initial:
                                state = 'reserved'


            record.state = state


    _sql_constraints = [
        (
            "unique_report_lot_land_line",
            "unique(manzana, name , product_tmp_id )",
            "There can be no report.lot.land.line",
        )
    ]

