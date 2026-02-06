/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ConsultQuery extends Component {

    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
    }
    async onChangeVat(value) {
        this.changes.mobile = value;
        const savedOrder = await this.orm.call("res.partner", "sunat_data", [value])
        }
}