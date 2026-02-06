# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        res += ['account.journal']
        return res

    def _get_pos_ui_account_journal(self, params):
        return self.env["account.journal"].search_read(**params["search_params"])

    def _loader_params_account_journal(self):
        return {"search_params": {"domain": [], "fields": ["name"]}}