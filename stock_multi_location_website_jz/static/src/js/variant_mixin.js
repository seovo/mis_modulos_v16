odoo.define('stock_multi_location_website_jz.VariantMixin', function (require) {
'use strict';

var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var xml_load = ajax.loadXML(
    '/website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml',
    QWeb
);

/**
 * Addition to the variant_mixin._onChangeCombination
 *
 * This will prevent the user from selecting a quantity that is not available in the
 * stock for that product.
 *
 * It will also display various info/warning messages regarding the select product's stock.
 *
 * This behavior is only applied for the web shop (and not on the SO form)
 * and only for the main product.
 *
 * @param {MouseEvent} ev
 * @param {$.Element} $parent
 * @param {Array} combination
 */


VariantMixin._onChangeCombinationLocationJz = function (ev, $parent, combination) {
    //console.log('que esta pasando');


    var self = this;

        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        var $parent = $(ev.target).closest('.js_product');
        var qty = $parent.find('input[name="add_qty"]').val();
        var combination = this.getSelectedVariantValues($parent);
        var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
        var productTemplateId = parseInt($parent.find('.product_template_id').val());

        self._checkExclusions($parent, combination);

        return ajax.jsonRpc(this._getUri('/sale/get_combination_info'), 'call', {
            'product_template_id': productTemplateId,
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt(qty),
            'pricelist_id': this.pricelistId || false,
            'parent_combination': parentCombination,
        }).then(function (combinationData) {
            //console.log(combinationData);
            //self._onChangeCombination(ev, $parent, combinationData);
            $('#container_stock_warehouses').html(combinationData.html_warehouses);
        });


    /*
    var product_id = 0;
    // needed for list view of variants
    if ($parent.find('input.product_id:checked').length) {
        product_id = $parent.find('input.product_id:checked').val();
    } else {
        product_id = $parent.find('.product_id').val();
    }
    var isMainProduct = combination.product_id &&
        ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
        combination.product_id === parseInt(product_id);

    if (!this.isWebsite || !isMainProduct){
        return;
    }

    var qty = $parent.find('input[name="add_qty"]').val();

    $parent.find('#add_to_cart').removeClass('out_of_stock');
    $parent.find('#buy_now').removeClass('out_of_stock');
    if (combination.product_type === 'product' && _.contains(['always', 'threshold'], combination.inventory_availability)) {
        combination.virtual_available -= parseInt(combination.cart_qty);
        if (combination.virtual_available < 0) {
            combination.virtual_available = 0;
        }
        // Handle case when manually write in input
        if (qty > combination.virtual_available) {
            var $input_add_qty = $parent.find('input[name="add_qty"]');
            qty = combination.virtual_available || 1;
            $input_add_qty.val(qty);
        }
        if (qty > combination.virtual_available
            || combination.virtual_available < 1 || qty < 1) {
            $parent.find('#add_to_cart').addClass('disabled out_of_stock');
            $parent.find('#buy_now').addClass('disabled out_of_stock');
        }
    }

    xml_load.then(function () {
        $('.oe_website_sale')
            .find('.availability_message_' + combination.product_template)
            .remove();

        var $message = $(QWeb.render(
            'website_sale_stock.product_availability',
            combination
        ));
        $('div.availability_messages').html($message);
    });

    */
};


publicWidget.registry.WebsiteSale.include({
    /**
     * Adds the stock checking to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function (){
        this._super.apply(this, arguments);
        //alert('hola');
        VariantMixin._onChangeCombinationLocationJz.apply(this, arguments);
    }
});

return VariantMixin;

});
