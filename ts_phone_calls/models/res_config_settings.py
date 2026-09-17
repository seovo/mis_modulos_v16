from odoo import api, exceptions, fields, models


class ResConfigSetting(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'
