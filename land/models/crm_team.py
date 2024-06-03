from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    commission_land   = fields.Float(string="Comission Terreno")
    #percentage_overrun_sale             = fields.Float(string="Porcentage Monto Sobrecosto")
