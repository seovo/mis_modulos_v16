from odoo import api, fields, models , _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):

        res = super(ResPartner, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)

        if not res:
            product_ids = self._search([('vat', 'ilike', name)], limit=limit,
                                       access_rights_uid=name_get_uid)
            return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))

        return res

