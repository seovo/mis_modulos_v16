from odoo import api, models, fields, _


class PlanningRole(models.Model):
    _inherit = 'planning.role'
    type_role = fields.Selection([('install','Instalación'),('uninstall','Desistalación')])