from odoo import api, fields, models , _

dx = {
    'single': 'Soltero' ,
    'married' : 'Casado' ,
    'cohabitant' : 'Conviviente Legal' ,
    'widower' : 'Viudo' ,
    'divorced' : 'Divorciado'
}

class ResPartner(models.Model):
    _inherit = 'res.partner'



    marital = fields.Selection(list(dx.items()), string='Marital Status',  tracking=True)

    def get_values_marital(self):
        return dx

    def get_array_marital(self):
        return list(self.get_values_marital().items())



    '''

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):

        res = super(ResPartner, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)

        if not res:
            product_ids = self._search([('vat', 'ilike', name)], limit=limit,
                                       access_rights_uid=name_get_uid)
            return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))

        return res
        
    '''

