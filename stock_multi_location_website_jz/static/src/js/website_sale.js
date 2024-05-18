/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';
import { jsonrpc } from "@web/core/network/rpc_service";

WebsiteSale.include({

    start() {
        const def = this._super(...arguments);

        //this.$('.js_main_product [data-attribute_exclusions]').change();
        //this.$('input .js_product_change').click();
        return def;
    },


    onChangeVariant: function (ev) {

         this._super(...arguments);



        var $parent = $(ev.target).closest('.js_product');
        if($parent.length){

            var productId = parseInt($('.product_id').val()) ;

            console.log(productId);

            const combination = this.getSelectedVariantValues($parent);
            let parentCombination;

            jsonrpc('/website_sale/get_combination_info', {
            'product_template_id': parseInt($parent.find('.product_template_id').val()),
            //'product_id': this._getProductId($parent),
            'product_id': productId ,
            'combination': combination,
            'add_qty': parseInt($parent.find('input[name="add_qty"]').val()),
            'parent_combination': parentCombination,
            'context': this.context,
            ...this._getOptionalCombinationInfoParam($parent),
        }).then((combinationData) => {
            //alert('que esta pasando aqui');
            //console.log(combinationData.html_warehouses);

            //this.$('.js_main_product [data-attribute_exclusions]').change();
            $('#container_stock_warehouses').html(combinationData.html_warehouses);
            //console.log($('#container_stock_warehouses').html());
            });


        }








    },

});



