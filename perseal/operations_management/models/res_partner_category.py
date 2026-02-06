# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    def unlink(self):
        for record in self:
            if record in [
                self.env.ref('operations_management.res_partner_category_TVF'),
                self.env.ref('operations_management.res_partner_category_TVC'),
                self.env.ref('operations_management.res_partner_category_TROC'),
                self.env.ref('operations_management.res_partner_category_TROD'),
                self.env.ref('operations_management.res_partner_category_TROP')
            ]:
                raise UserError('No se puede eliminar este tipo de categoría ya que es fundamental en el flujo Anka.')
        return super(ResPartnerCategory, self).unlink()
