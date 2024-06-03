from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    commission_land   = fields.Float(string="Comission Terreno")
    type_period_comission = fields.Selection([('month','Mensual'),('week','Semanal')],string="Periodo Commision")
    number_sale_additional_commision = fields.Integer(string="# Ventas Commisión Adicional")
    amount_sale_additional_commision = fields.Integer(string="Monto Commisión Adicional")
    members_additional_commision = fields.Many2many('res.users',string="Miembros Comission Adicional")
    #percentage_overrun_sale             = fields.Float(string="Porcentage Monto Sobrecosto")
