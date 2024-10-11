from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    commission_land   = fields.Float(string="Comission Terreno")
    type_period_comission = fields.Selection([
        ('month','Mensual'),
        ('half', 'Quincenal'),
        ('week','Semanal')],string="Periodo Commision")
    number_sale_additional_commision = fields.Integer(string="# Ventas Commisión Adicional")
    amount_sale_additional_commision = fields.Integer(string="Monto Commisión Adicional")
    members_additional_commision = fields.Many2many('res.users',string="Miembros Comission Adicional")
    number_sale_discount_commision = fields.Integer(string="# Ventas Descuento Commisión")
    percentage_sale_discount_commision = fields.Float(string="% Monto Descuento Commisión",default="50")
    comission_ids = fields.One2many('commission.land','team_id')


    def show_comisiones_land(self):
        return {
            "name": f"COMISIONES {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            #"view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "commission.land",
            #"res_id": self.id,
            "target": "current",
            "domain": [('team_id','=',self.id)] ,
            "context": {
                'search_default_group_user_id': 1
            }

        }

    def get_show_comisiones_land(self):

        date = fields.Datetime.now().date()

        for user in self.member_ids:
            new_com = self.env['commission.land'].new({
                'name': 'NEW' ,
                'date_commission': date ,
                'date_start': date ,
                'date_end': date ,
                'user_id':  user.id ,
                'team_id': self.id ,
                'type_period_comission': self.type_period_comission
            })

            new_com.onchange_user_id()
            new_com.onchange_lines()

            if not new_com.line_ids:
                new_com.unlink()
                continue
            new_com.set_sequence()



        return  self.show_comisiones_land()
