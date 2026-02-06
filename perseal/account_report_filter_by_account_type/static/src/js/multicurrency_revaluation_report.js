/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { MulticurrencyRevaluationReportFilters } from "@account_reports/components/multicurrency_revaluation_report/filters/filters";

patch(MulticurrencyRevaluationReportFilters.prototype, {
    async filterExchangeRate() {
        Object.values(this.controller.options.currency_rates).forEach((currencyRate) => {
            const input = document.querySelector(`input[name="${ currencyRate.currency_id }"]`);

            currencyRate.rate = 1/input.value;
        });

        this.controller.reload('currency_rates', this.controller.options);
    }
});
