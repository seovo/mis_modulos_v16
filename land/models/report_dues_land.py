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
    mounth_expired = fields.Integer(string="Meses Vencidos >=")
    days_expired = fields.Integer(string="Dias Vencidos >=")


    order_ids = fields.Many2many('sale.order',string="Ventas")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    dues_max = fields.Integer(compute='get_dues_max')
    dues_payment_max = fields.Integer(compute='get_dues_max')
    stage_land = fields.Selection([
        ('signed', ('Firmado')),
        ('preaviso', ('Carta Preaviso')),
        ('cancel', ('Resuelto')),
        ('regularizado', 'Regularizado'),
    ], string="Estado Terreno")

    stage_payment_lan = fields.Selection([
        ('separation', 'Separado'),
        ('initial', 'Inicial Incompletada'),
        ('dues', 'Cuotas Pendientes'),
        ('payment', 'Pagando Cuotas'),
        ('completed', 'Cuotas Completada')
    ], string='Etapa Pago  Terreno')




    def action_preview_lines(self):
        self.update_data()
        self.order_ids.update_credit_saldo()
        self.order_ids._get_stage_payment_land()

        return {
            "name": f"Ventas",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "view_id": self.env.ref('land.view_order_tree_report').id,
            "res_model": "sale.order",
            #"res_id": product.id,
            "target": "current",
            "domain": [('id', 'in', self.order_ids.ids)],
            #"context": {
            #    'search_default_gr_mz_value_id': 1
            #}

        }

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

    @api.onchange('type_periodo_invoiced','seller_land_id','mounth_expired','days_expired','stage_payment_lan')
    def update_data(self):

        for record in self:
            record.order_ids = False
            domain = [('nro_internal_land','!=',False),
                      ('seller_land_id','in',record.seller_land_id.ids),
                      ('mounth_expired_land','>=',record.mounth_expired),
                      #('days_expired_land','>=',record.days_expired)
                      ]
            if record.type_periodo_invoiced != 'half_month_end_month':
                domain.append(('type_periodo_invoiced','=',record.type_periodo_invoiced))



            if record.stage_land:
                domain.append(('stage_land','=',record.stage_land))
            sales = self.env['sale.order'].search(domain)

            sale_ids = []


            for sale in sales:
                if record.days_expired and record.days_expired > 0 :
                    if not sale.days_expired_land >= record.days_expired :
                        continue

                        # if not sale.schedule_land_ids:
                sale.update_schedule()
                sale._get_stage_payment_land()

                if record.stage_payment_lan:
                    if record.stage_payment_lan != sale.stage_payment_lan:
                        continue

                sale_ids.append(sale.id)




            record.order_ids = [(6,0,sale_ids)] if sale_ids else None