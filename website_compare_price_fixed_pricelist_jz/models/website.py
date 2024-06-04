from odoo import _, _lt, SUPERUSER_ID, api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

class Website(models.Model):
    _inherit = 'website'

    def get_pricelist_available(self, show_visible=False):
        res = super().get_pricelist_available(show_visible=show_visible)


        pricelist_ids = []
        for pricelist in res:
            available = False
            for price_list_item in pricelist.item_ids:
                if self.env['product.template'].validate_range_pricelist_jz(price_list_item):
                    available = True

            if available:
                pricelist_ids.append(pricelist.id)

        return self.env['product.pricelist'].browse(pricelist_ids)


    def _get_current_pricelist(self):



        """
        :returns: The current pricelist record
        """
        self = self.with_company(self.company_id)
        ProductPricelist = self.env['product.pricelist']

        pricelist = ProductPricelist
        if request and request.session.get('website_sale_current_pl'):
            # `website_sale_current_pl` is set only if the user specifically chose it:
            #  - Either, he chose it from the pricelist selection
            #  - Either, he entered a coupon code
            pricelist = ProductPricelist.browse(request.session['website_sale_current_pl']).exists().sudo()
            country_code = self._get_geoip_country_code()
            if not pricelist or not pricelist._is_available_on_website(self) or not pricelist._is_available_in_country(country_code):
                request.session.pop('website_sale_current_pl')
                pricelist = ProductPricelist



        if not pricelist:
            partner_sudo = self.env.user.partner_id

            # If the user has a saved cart, it take the pricelist of this last unconfirmed cart
            pricelist = partner_sudo.last_website_so_id.pricelist_id
            if not pricelist:
                # The pricelist of the user set on its partner form.
                # If the user is not signed in, it's the public user pricelist
                pricelist = partner_sudo.property_product_pricelist

            # The list of available pricelists for this user.
            # If the user is signed in, and has a pricelist set different than the public user pricelist
            # then this pricelist will always be considered as available
            available_pricelists = self.get_pricelist_available()

            if available_pricelists and pricelist not in available_pricelists:
                #raise ValueError(available_pricelists)
                # If there is at least one pricelist in the available pricelists
                # and the chosen pricelist is not within them
                # it then choose the first available pricelist.
                # This can only happen when the pricelist is the public user pricelist and this pricelist is not in the available pricelist for this localization
                # If the user is signed in, and has a special pricelist (different than the public user pricelist),
                # then this special pricelist is amongs these available pricelists, and therefore it won't fall in this case.
                pricelist = available_pricelists[0]

        return pricelist



