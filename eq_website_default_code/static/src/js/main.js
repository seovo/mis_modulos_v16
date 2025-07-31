/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale";

VariantMixin._onChangeProductDefaultcode = function (ev, $parent, combination) {
	var $default_code = $parent.find('.default_code');
	$default_code.text(combination.default_code || '');
};


publicWidget.registry.WebsiteSale.include({
	/**
     * show Product internal reference to the regular _onChangeCombination method
     * @override
     */
	_onChangeCombination: function () {
		this._super.apply(this, arguments);
		VariantMixin._onChangeProductDefaultcode.apply(this, arguments);
	}
});

export default VariantMixin;