from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from datetime import date, timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):

        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group(
                'account.group_account_invoice') and not self.env.user.has_group('l10n_pe_pos.group_pos_cajero'):
            raise AccessError(_("You don't have the access rights to post an invoice."))

        if self.env.user.has_group('l10n_pe_pos.group_pos_cajero') and not self.env.user.has_group(
                'account.group_account_invoice'):

            # Se agrega el grupo group_account_invoice al usuario se llama la funcion post y luego se le quita
            # el grupo al usurio. Esto es para poder cerrar y validar
            self.env.user.groups_id += self.env.ref('account.group_account_invoice')
            res = super(AccountMove, self).post()
            user_groups_id = self.env.user.groups_id
            self.env.user.groups_id = self.env['res.groups']
            for group in user_groups_id:
                if group != self.env.ref('account.group_account_invoice'):
                    self.env.user.groups_id += group

            return res

        else:
            return super(AccountMove, self).post()
