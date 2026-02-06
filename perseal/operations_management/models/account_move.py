# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountMove(models.Model):

    _inherit = "account.move"
    
    operacion_id = fields.Many2one(
        comodel_name='operacion.operacion',
        string='Operación',
    )
    
    def action_post(self):
        res = super().action_post()
        if self.operacion_id:
            self.operacion_id.action_state_titularizada()
        return res
    
    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        if self.operacion_id:
            self.operacion_id.action_state_titularizada()
        return posted