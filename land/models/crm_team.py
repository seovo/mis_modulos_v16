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
            "res_model": "commission.land",
            "target": "current",
            "domain": [('team_id','=',self.id)] ,
            "context": {
                'search_default_group_state': 1 ,
                'search_default_group_user_id': 1
            }

        }

    def get_show_comisiones_land(self):

        date = fields.Datetime.now().date()

        for user in self.member_ids:

            exist_com = self.env['commission.land'].search([('date_commission','=',date)])
            if exist_com:
                continue

            new_com = self.env['commission.land'].create({
                'name': 'NEW' ,
                'date_commission': date ,
                'date_start': date ,
                'date_end': date ,
                'user_id':  user.id ,
                'team_id': self.id ,
                'type_period_comission': self.type_period_comission ,
            })

            new_com.onchange_user_id()
            new_com.change_type_period_comission()
            new_com.change_date_start()
            new_com.onchange_lines()


            if not new_com.line_ids:
                new_com.unlink()
                continue
            new_com.set_sequence()
            new_com.calculate_totals()

        return  self.show_comisiones_land()
