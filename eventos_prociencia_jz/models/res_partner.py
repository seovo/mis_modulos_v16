from odoo import models, exceptions, fields , api , _
from odoo.exceptions import UserError
from collections import defaultdict

class ResPartner(models.Model):
    _inherit = "res.partner"

    def signup_get_auth_param(self):
        """ Get a signup token related to the partner if signup is enabled.
            If the partner already has a user, get the login parameter.
        """
        #if not self.env.user._is_internal() and not self.env.is_admin():
        #    raise exceptions.AccessDenied()

        res = defaultdict(dict)

        allow_signup = self.env['res.users']._get_signup_invitation_scope() == 'b2c'
        for partner in self:
            partner = partner.sudo()
            if allow_signup and not partner.user_ids:
                partner.signup_prepare()
                res[partner.id]['auth_signup_token'] = partner.signup_token
            elif partner.user_ids:
                res[partner.id]['auth_login'] = partner.user_ids[0].login
        return res