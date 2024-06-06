odoo.define('payment_nuvei.payment', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;
    // var base = require('web_editor.base');
    var PaymentCheckoutForm = require('payment.checkout_form');

    /**
    * Search for target view with jquery selector and initialize elements
    * if we are in inovice details view, otherwise ignore
    */
    PaymentCheckoutForm.include({

        willStart: function () {
            return this._super.apply(this, arguments).then(function () {
                return ajax.loadJS("https://cdn.paymentez.com/checkout/1.0.1/paymentez-checkout.min.js");
            })
        },
        /*
        * Ejecuta la logica de paymentez para levantar el modal de pago
        */
        launch_paymentez_modal: function (processingValues) {
            var $form = $(processingValues.redirect_form_html);
            var $mainForm = $(this.el);
            var client_app_code = $form.find('input[name="nuvei_client_app_code"]').val();
            var client_app_key = $form.find('input[name="nuvei_client_app_key"]').val();
            var environment = $form.find('input[name="environment"]').val();
            var reference = processingValues.reference;
            var order_id = $mainForm.attr('data-order-id');
            var invoice_id = $mainForm.attr('data-invoice-id');
            var on_response = false;

            var paymentezCheckout = new PaymentezCheckout.modal({
                client_app_code: client_app_code, // Client Credentials Provied by Paymentez
                client_app_key: client_app_key, // Client Credentials Provied by Paymentez
                locale: 'es', // User's preferred language (es, en, pt). English will be used by default.
                env_mode: environment == 'test' ? 'stg' : 'prod', // `prod`, `stg`, `dev`, `local` to change environment. Default is `stg`
                onResponse: function (response) { // The callback to invoke when the Checkout process is completed
                    on_response = true;
                    if ("error" in response) {
                        // Connection error or other non payment related error, do not send submit
                        Dialog.alert(self, _t(response['error']['type']) + ' ' + response['error']['help'] + ' ' + response['error']['description']);
                    } else if ("transaction" in response) {
                        // Payment process succeed
                        var transaction_status = $('<input type="hidden" name="transaction_status" value="' + response['transaction']['status'] + '"/>');
                        var transaction_id = $('<input type="hidden" name="transaction_id" value="' + response['transaction']['id'] + '"/>');
                        var transaction_status_detail = $('<input type="hidden" name="transaction_status_detail" value="' + response['transaction']['status_detail'] + '"/>');
                        var transaction_reference = $('<input type="hidden" name="reference" value="' + response['transaction']['dev_reference'] + '"/>');
                        if ('authorization_code' in response['transaction']) {
                            var transaction_authorization_code = $('<input type="hidden" name="transaction_authorization_code" value="' + response['transaction']['authorization_code'] + '"/>');
                            $form.append(transaction_authorization_code);
                        }
                        $form.append(transaction_status);
                        $form.append(transaction_id);
                        $form.append(transaction_status_detail);
                        $form.append(transaction_reference);
                        $(document.body).append($form);
                        $form.submit();
                    } else {
                        // Unexpected error
                        return false;
                    }

                },
                onClose: function () {
                    if (!on_response) {
                        window.location.reload();
                    }
                },
            });
            // Close Checkout on page navigation:
            window.addEventListener('popstate', function () {
                paymentezCheckout.close();
            });
            return ajax.jsonRpc('/payment/nuvei/get_submit_data', 'call',
                {
                    'user_fields': ['id', 'email', 'phone'],
                    'order_fields': ['amount_total', 'amount_tax',
                        'amount_iva_taxable', 'tax_percentage'],
                    'order_id': order_id,
                    'invoice_id': invoice_id
                }
            ).then(function (data) {
                if (data == undefined) {
                    // Connection error or other non payment related error, do not send submit
                    Dialog.alert(
                        self, _t('An error ocurred when try to get order and user data.')
                    );
                    return { 'error': true };
                }
                if (data['error']) {
                    // Already paid order, do not send submit
                    Dialog.alert(
                        self, _t('This order is already paid.')
                    );
                    return { 'error': true };
                }
                paymentezCheckout.open({
                    user_id: data['user_data']['id'].toString() || '1',//Default admin
                    user_email: data['user_data']['email'] || '', //optional
                    user_phone: data['user_data']['phone'] || '', //optional
                    order_description: reference,
                    order_amount: data['order_data']['amount_total'],
                    order_vat: data['order_data']['amount_tax'],
                    order_taxable_amount: data['order_data']['amount_iva_taxable'],
                    order_tax_percentage: data['order_data']['tax_percentage'],
                    order_reference: reference,
                    order_installments_type: 0,

                });
                //Hide odoo enterprise block ui
                $('div.blockUI').hide();
            });

        },
        _processPayment: function (provider, paymentOptionId, flow) {
            var self = this;
            if (provider === 'nuvei') {
                return this._rpc({
                    route: this.txContext.transactionRoute,
                    params: this._prepareTransactionRouteParams(provider, paymentOptionId, flow),
                }).then(processingValues => {
                    self.launch_paymentez_modal(processingValues);
                }).guardedCatch(error => {
                    error.event.preventDefault();
                    this._displayError(
                        _t("Server Error"),
                        _t("We are not able to process your payment."),
                        error.message.data.message
                    );
                });
            } else {
                return this._super(...arguments);
            }
        },
    });
});
