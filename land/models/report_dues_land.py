from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date

class CommissionRiman(models.Model):
    _name        = 'report.dues.land'
    _description = 'report.dues.land'
    name         = fields.Char(required=True)
    type_periodo_invoiced = fields.Selection([
        ('half_month', 'Quincenal'),
        ('end_month', 'Fin de Mes'),
        ('half_month_end_month', 'Quincenal y Fin de Mes'),
    ],
     string="Periodo de Facturación",
        required=True
    )
    seller_land_id = fields.Many2many('seller.land', string="Proveedores", required=True)
    order_ids = fields.Many2many('sale.order',string="Ventas")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    dues_max = fields.Integer(compute='get_dues_max')
    dues_payment_max = fields.Integer(compute='get_dues_max')

    @api.depends('order_ids')
    def get_dues_max(self):
        for record in self:
            dues_max = 0
            count_payment_max = 0
            for order in record.order_ids:
                if order.dues_land > dues_max :
                    dues_max = order.dues_land

                count_payment = 0

                for line in order.schedule_land_ids:
                    if line.is_paid:
                        count_payment += 1

                if count_payment > count_payment_max :
                    count_payment_max = count_payment

            record.dues_payment_max  = count_payment_max
            record.dues_max = dues_max

    @api.onchange('type_periodo_invoiced','seller_land_id')
    def update_data(self):
        for record in self:
            record.order_ids = False
            domain = [('nro_internal_land','!=',False),('seller_land_id','in',record.seller_land_id.ids)]
            if record.type_periodo_invoiced != 'half_month_end_month':
                domain.append(('type_periodo_invoiced','=',record.type_periodo_invoiced))
            sales = self.env['sale.order'].search(domain)
            for sale in sales:
                if not sale.schedule_land_ids:
                    sale.update_schedule()
            record.order_ids = [(6,0,sales.ids)]