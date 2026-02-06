# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    @api.model
    def create(self, vals):
        res = super(LoyaltyReward, self).create(vals)
        if res.discount_product_id and res.reward_type == 'discount' and res.discount_apply_on == 'on_order':
            res.discount_product_id.product_tmpl_id.is_gobal_discount = True
        return res

    def write(self, vals):
        if vals.get('discount_product_id'):
            self.discount_product_id.product_tmpl_id.is_gobal_discount = False
        res = super(LoyaltyReward, self).write(vals)
        if self.discount_product_id and self.reward_type == 'discount' and self.discount_apply_on == 'on_order':
            self.discount_product_id.product_tmpl_id.is_gobal_discount = True
        return res

    def unlink(self):
        if self.discount_product_id and self.reward_type == 'discount' and self.discount_apply_on == 'on_order':
            self.discount_product_id.product_tmpl_id.is_gobal_discount = False
        return super(LoyaltyReward, self).unlink()