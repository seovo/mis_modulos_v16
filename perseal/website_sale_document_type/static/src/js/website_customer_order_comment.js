/** @odoo-module */
import PublicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from '@web/core/network/rpc_service';

export const Comment = PublicWidget.Widget.extend({
    selector: "#customer_comment",

    start() {
        $('button[name="o_payment_submit_button"]').bind("click",function(ev){
            if ($('#customer_comment')[0].checked){
                var customer_comment = $('#customer_comment').val();
                jsonrpc("/shop/customer_comment/",{
                    'comment': customer_comment}
                );
            }else{
                var customer_comment = 'factura';
                jsonrpc("/shop/customer_comment/",{
                    'comment': customer_comment
                });
            }

        });
    },    
});

PublicWidget.registry.Comment =  Comment;
