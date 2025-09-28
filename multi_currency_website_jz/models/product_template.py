from odoo import fields, models , api

'''
class ProductTemplate(models.Model):
    _inherit = 'res.company'

    @api.model
    def _get_main_company(self):

        return self.env['res.company'].sudo().search([('id','=',2)], limit=1, order="id")

        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")

        return main_company
        
'''

class ProductTemplate(models.Model):
    _inherit = 'product.template'





    @api.depends('company_id')
    def _compute_currency_id(self):

        res = super(ProductTemplate, self)._compute_currency_id()

        default_currency = self.env['res.currency'].search(
            [('is_default_without_company','=',True)],limit=1
        )

        if default_currency:
            for product in self:
                if not product.company_id:
                    product.currency_id = default_currency.id
