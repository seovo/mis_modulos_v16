from odoo import api, models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    resource_jz_id = fields.Many2one('resource.resource',string="Guardia")
    role_jz_id = fields.Many2one('planning.role',string="Sector")

