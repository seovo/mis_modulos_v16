from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    datawave_sigma_days = fields.Integer('Días usados para Sigma tienda',config_parameter='datawave.ventana_sigma_dias')
