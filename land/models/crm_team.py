from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    percentage_total_base_sale          = fields.Float(string="Porcentage Monto Base")
    #percentage_overrun_sale             = fields.Float(string="Porcentage Monto Sobrecosto")
