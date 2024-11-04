/** @odoo-module */
import PublicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from '@web/core/network/rpc_service';

export const DatePicker = PublicWidget.Widget.extend({
    selector: "#delivery_date",
    
    start() {
        $('#delivery_date').attr('min', new Date().toISOString().split('T')[0])
        $('button[name="o_payment_submit_button"]').bind("click", function(ev) {
            var customer_order_delivery_date = $('#delivery_date').val();
            var customer_order_delivery_comment = $('#delivery_comment').val();
            jsonrpc("/shop/customer_order_delivery", {
                'delivery_date': customer_order_delivery_date,
                'delivery_comment': customer_order_delivery_comment
            });  
        });
    },    
});

PublicWidget.registry.DatePicker =  DatePicker;
