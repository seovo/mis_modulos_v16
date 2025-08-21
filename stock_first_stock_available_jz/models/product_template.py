from odoo import models



class ProductTemplate(models.Model):
    _inherit = 'product.template'


    def _get_first_possible_combination2(self, parent_combination=None, necessary_values=None):

        try:


            products = self.product_variant_ids

            product_stock_mayor = None
            quantity_stock_mayor = 0

            for product in products:
                combination = product.product_template_attribute_value_ids

                combination_info = self._get_combination_info(combination, add_qty=1)

                free_qty = combination_info.get('free_qty')

                if free_qty >  quantity_stock_mayor :
                    quantity_stock_mayor = free_qty
                    product_stock_mayor = product


            if quantity_stock_mayor > 0 :
                return  product_stock_mayor.product_template_attribute_value_ids
            else:
                return self._get_first_possible_combination(parent_combination,necessary_values)
        except:

            return self._get_first_possible_combination(parent_combination,necessary_values)


