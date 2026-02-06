/** @odoo-module */
import {patch} from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async _postPushOrderResolve(order, order_server_ids) {
        const savedOrder = await this.orm.searchRead(
            "pos.order",
            [["id", "in", order_server_ids]],
            ["invoice_number", "order_document_type"]
        );
        order.invoice_name = savedOrder[0].invoice_number;
        order.order_document_type = savedOrder[0].order_document_type;
        return super._postPushOrderResolve(...arguments);
    },
});