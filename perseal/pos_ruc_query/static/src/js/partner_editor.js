/** @odoo-module */

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(PartnerDetailsEdit.prototype, {

    setup() {
        const res = super.setup(...arguments);
        this.orm = useService("orm");
        return res;
    },
    async onChangeVat(value) {
        const dict_values = await this.orm.call("res.partner", "sunat_data", [value]);
        if (dict_values != false) {
            this.changes.name = dict_values.nombre;
            this.changes.city_id = dict_values.province_id;
            this.changes.country_id = dict_values.country_id;
            this.changes.l10n_latam_identification_type_id = dict_values.doc_type;

            this.changes.l10n_pe_district = dict_values.district_id;
            this.changes.state_id = dict_values.state_id;
            this.changes.street = dict_values.street;
            this.changes.zip = dict_values.ubigeo;
        }else{
            this.changes.name = "";
        }
        }
});