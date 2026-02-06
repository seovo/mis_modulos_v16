/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import {
    formatDate,
    formatDateTime,
    serializeDateTime,
    deserializeDate,
    deserializeDateTime,
} from "@web/core/l10n/dates";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(...arguments);
            if (order) {
                result.partner = order.get_partner();
                result.invoice_name = order.invoice_name;
                result.order_document_type = order.order_document_type || 'Recibo';
                result.receipt_date = formatDate(order.date_order).replaceAll("/","-");
            }
        return result;
    },
});