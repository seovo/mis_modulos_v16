from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name    = 'product.template'

    def validate_range_pricelist_jz(self,price_list_item):
        date_now = fields.Datetime.now()

        date_start_range = True
        date_end_range = True

        if not price_list_item.date_start and not price_list_item.date_end:
            return price_list_item



        if price_list_item.date_start:

            if date_now < price_list_item.date_start:
                date_start_range = False

        if price_list_item.date_end:
            if date_now > price_list_item.date_end:
                date_end_range = False

        if date_start_range and date_end_range:
            return price_list_item


    def get_pricelist_depend_jz(self,pricelist, res):

        domain = [('pricelist_id', '=', int(pricelist.id)), ('compute_price', '=', 'fixed')]

        domainx = domain + [('product_id', '=', int(res['product_id']))]
        price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)



        if price_list_item:
            return self.validate_range_pricelist_jz(price_list_item)


        else:
            domainx = domain + [('product_tmpl_id', '=', int(res['product_template_id']))]
            price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
            if price_list_item:
                return self.validate_range_pricelist_jz(price_list_item)


            else:
                product_template = self.env['product.template'].browse(int(res['product_template_id']))
                domainx = domain + [('categ_id', '=', product_template.categ_id.id)]
                price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                if price_list_item:
                    return self.validate_range_pricelist_jz(price_list_item)
                else:
                    domainx = domain + [('applied_on', '=', '3_global')]
                    price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                    if price_list_item:
                        return self.validate_range_pricelist_jz(price_list_item)

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

            domain = [('pricelist_id', '=', int(pricelist.id)), ('base','=','pricelist') ,('compute_price', '=', 'formula')]
            domainx = domain+[('product_id','=',int(res['product_id']))]
            price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)

            #raise ValidationError(self.validate_range_pricelist_jz(price_list_item))

            if price_list_item and price_list_item.base_pricelist_id:

                price_list_itemx = self.get_pricelist_depend_jz(price_list_item.base_pricelist_id, res)
                if price_list_itemx:

                    res['compare_list_price'] = price_list_itemx.fixed_price

            else:
                domainx = domain + [('product_tmpl_id', '=', int(res['product_template_id']))]
                price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                if price_list_item and price_list_item.base_pricelist_id:

                    price_list_itemx = self.get_pricelist_depend_jz(price_list_item.base_pricelist_id, res)

                    if price_list_itemx:
                        res['compare_list_price'] = price_list_itemx.fixed_price
                else:
                    product_template = self.env['product.template'].browse(int(res['product_template_id']))
                    domainx = domain + [('categ_id', '=', product_template.categ_id.id)]
                    price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                    if price_list_item and price_list_item.base_pricelist_id:
                        price_list_itemx = self.get_pricelist_depend_jz(price_list_item.base_pricelist_id, res)
                        if price_list_itemx:
                            res['compare_list_price'] = price_list_itemx.fixed_price
                    else:
                        domainx = domain + [('applied_on', '=', '3_global')]
                        price_list_item = self.env['product.pricelist.item'].search(domainx, limit=1)
                        if price_list_item and price_list_item.base_pricelist_id:
                            price_list_itemx = self.get_pricelist_depend_jz(price_list_item.base_pricelist_id, res)
                            if price_list_itemx:
                                res['compare_list_price'] = price_list_itemx.fixed_price





        return res
