/** @odoo-module */
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.journal_ids_from_config = this.pos.account_journal_ids.filter((method) =>
            this.pos.config.invoice_journal_ids.includes(method.id)
        );
    },
    SetDefaultInvoice(journal_id) {
        if(this.currentOrder.invoice_journal_id == journal_id || this.currentOrder.is_to_invoice() == false){
			this.currentOrder.set_to_invoice(!this.currentOrder.is_to_invoice());
		}
        this.currentOrder.invoice_journal_id = journal_id;
    }
});

patch(Order.prototype, {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json['invoice_journal_id'] = this.invoice_journal_id ? this.invoice_journal_id : undefined;
        return json;
    },
});