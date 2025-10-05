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


    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        res = super(ProductTemplate, self)._get_additionnal_combination_info(product_or_template, quantity, date, website)

        pricelist = website.pricelist_id

        pricelists = self.env['product.pricelist'].search([
            ('selectable','=',True),('id','!=',pricelist.id),'|',
            ('website_id','=',website.id),('website_id','=',False)
        ])

        prices = []
        labels = []
        li_html = ''
        for pri in pricelists:

            pricelist_price = pri._get_product_price(
                product=product_or_template,
                quantity=quantity,
                target_currency=pri.currency_id,
            )

            prices.append({
                'price': pricelist_price ,
                'currency': pri.currency_id.display_name
            })

            price_format = "{:,.2f}".format(pricelist_price)

            labels.append(f'''<span style="margin-left: 0.5rem;">{pri.currency_id.symbol}{price_format}</span>''')
            li_html += f'''
            <li><a class="dropdown-item" href="/shop/change_pricelist/{pri.id}">{price_format} {pri.name}  </a></li>
            '''


        currency = website.currency_id

        html_prices = ''

        if prices:
            html_prices = f'''
        
        <a class="btn btn-light dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-bs-toggle="dropdown" aria-expanded="false">
          {" ".join(labels)}
        </a>
        
        <ul class="dropdown-menu" aria-labelledby="dropdownMenuLink">
          {li_html}
        </ul>

        '''

        res.update({
            'prices': prices ,
            'html_prices': html_prices if prices else ''
            #'data': 'ok',
            #'pricelist': pricelist ,
            #'currency': currency,  # displayed currency
            #'pricelists': pricelists
        })

        return res


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
