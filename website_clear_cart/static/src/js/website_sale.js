/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.websiteSaleCart.include({
    events: Object.assign({}, publicWidget.registry.websiteSaleCart.prototype.events, {
        'click .js_clear_shopping_cart': '_onClearCart',
    }),

    async _onClearCart(ev) {
        await jsonrpc("/shop/cart/clear");
        window.location = "/shop/cart";
    },
});
