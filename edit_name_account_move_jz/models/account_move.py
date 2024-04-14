from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def edit_name_jz(self):

        #raise ValidationError('OKA')
        view = self.env.ref('edit_name_account_move_jz.account_move_form')

        return {
            "name": f"EDIT NAME :   {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.move",
            "target": "new",
            "res_id": self.id,
            "view_id": view.id
        }
