/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AccountReportFilters } from "@account_reports/components/account_report/filters/filters";

patch(AccountReportFilters.prototype, {
   get selectedAccountType() {
        let selectedAccountType = this.controller.options.account_type.filter(accountType => accountType.selected);
        console.log('preuba')
        if (!selectedAccountType.length) { return _t("None"); }
        if (selectedAccountType.length === 5) { return _t("All"); }

        const accountTypeMappings = [
            {list: ['trade_receivable', 'non_trade_receivable'], name: _t('All Receivable')},
            {list: ['trade_payable', 'non_trade_payable'], name: _t('All Payable')},
            {list: ['trade_receivable', 'trade_payable'], name: _t('Trade Partners')},
            {list: ['non_trade_receivable', 'non_trade_payable'], name: _t('Non Trade Partners')},
            {list: ['bank', 'bank'], name: 'Banco y efectivo'},
        ]

        const listToDisplay = []
        for (const mapping of accountTypeMappings) {
            if (mapping.list.every(accountType => selectedAccountType.map(accountType => accountType.id).includes(accountType))) {
                listToDisplay.push(mapping.name);
                // Delete already checked id
                selectedAccountType = selectedAccountType.filter(accountType => !mapping.list.includes(accountType.id));
            }
        }

        return listToDisplay.concat(selectedAccountType.map(accountType => accountType.name)).join(', ')
    }
});