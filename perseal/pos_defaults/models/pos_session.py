# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_data_process(self, loaded_data):
        res = super()._pos_data_process(loaded_data)
        if self._is_pe_company():
            loaded_data["consumidor_final_anonimo_id"] = self.config_id.default_partner.id
        return res