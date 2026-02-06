odoo.define('account_report_extend.account_reports2', function (require) {
    'use strict';
    var AccountReportsWidget = require('account_reports.account_report');

    AccountReportsWidget.include({
        render_searchview_buttons: function(){
            this._super.apply(this, arguments);
            let self = this;
            _.each(this.$searchview_buttons.find('.js_cuenta_x_cobrar'), function(k) {
                $(k).toggleClass('selected', self.report_options[$(k).data('filter')]);
            });
            _.each(this.$searchview_buttons.find('.js_cuenta_x_pagar'), function(k) {
                $(k).toggleClass('selected', self.report_options[$(k).data('filter')]);
            });
            _.each(this.$searchview_buttons.find('.js_bank_x_cash'), function(k) {
                $(k).toggleClass('selected', self.report_options[$(k).data('filter')]);
            });
            this.$searchview_buttons.find('.js_cuenta_x_cobrar').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = !self.report_options[option_value];
                self.reload();
            });
            this.$searchview_buttons.find('.js_cuenta_x_pagar').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = !self.report_options[option_value];
                self.reload();
            });
            this.$searchview_buttons.find('.js_bank_x_cash').click(function (event) {
                var option_value = $(this).data('filter');
                self.report_options[option_value] = !self.report_options[option_value];
                self.reload();
            });
        },
    });

});