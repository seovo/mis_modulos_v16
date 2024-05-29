from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name    = 'product.template'

    def _get_combination_info(
            self, combination=False, product_id=False, add_qty=1.0,
            parent_combination=False, only_template=False,
    ):
        res = super()._get_combination_info(
            combination, product_id, add_qty ,
            parent_combination, only_template,
        )

        website = self.env['website'].get_current_website().with_context(self.env.context)

        pricelist = website.pricelist_id
        if pricelist:

            raise ValueError(pricelist)

            domain = [('pricelist_id','=',int(pricelist.id)),('compute_price','=','fixed')]

            domainx = domain+[('product_id','=',int(res['product_id']))]
            price_list_item =  self.env['product.pricelist.item'].search(domainx,limit=1)

            if price_list_item:
                res['compare_list_price'] = price_list_item.fixed_price
            else:
                domainx = domain + [('product_tmpl_id', '=', int(res['product_template_id']))]
                price_list_item = self.env['product.pricelist.item'].search(domainx,limit=1)
                if price_list_item:
                    res['compare_list_price'] = price_list_item.fixed_price
                else:
                    product_template = self.env['product.template'].browse(int(res['product_template_id']))
                    domainx = domain + [('categ_id', '=', product_template.categ_id.id)]
                    price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                    if price_list_item:
                        res['compare_list_price'] = price_list_item.fixed_price
                    else:
                        domainx = domain + [('applied_on', '=', '3_global')]
                        price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                        if price_list_item:
                            res['compare_list_price'] = price_list_item.fixed_price

        return res
