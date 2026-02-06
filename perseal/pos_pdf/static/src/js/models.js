/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    export_for_printing() {
            const receipt = super.export_for_printing(...arguments);
            receipt["customer"] = this.get_partner();
            return receipt;
        },

});
