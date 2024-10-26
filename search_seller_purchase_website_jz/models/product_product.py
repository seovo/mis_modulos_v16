from odoo import api, fields, models
from odoo import SUPERUSER_ID
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):

        res =  super(ProductTemplate, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)

        if not res:


            suppliers_ids = self.env['product.supplierinfo'].sudo()._search(['|','|',('name', 'ilike', name ),
                ('product_code', operator, name),
                ('product_name', operator, name)], limit=limit,access_rights_uid=name_get_uid)


            if suppliers_ids:
                product_ids = self._search([('seller_ids', 'in', suppliers_ids)], limit=limit,
                                           access_rights_uid=name_get_uid)
                return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))



        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):

        res =  super(ProductProduct, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)

        if not res:
            #suppliers_ids = self.env['product.supplierinfo']._search([
            #    ('name', 'ilike', name ),
            #    '|',
            #    ('product_code', operator, name),
            #    ('product_name', operator, name)], access_rights_uid=name_get_uid)

            suppliers_ids = self.env['product.supplierinfo'].sudo()._search(['|','|',('name', 'ilike', name ),
                ('product_code', operator, name),
                ('product_name', operator, name)], limit=limit,access_rights_uid=name_get_uid)


            if suppliers_ids:
                product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                           access_rights_uid=name_get_uid)
                return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))



        return res




