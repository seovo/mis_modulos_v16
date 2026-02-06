/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { EditListPopup } from "@point_of_sale/app/store/select_lot_popup/select_lot_popup";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    // @Override
    async getEditedPackLotLines(isAllowOnlyOneLot, packLotLinesToEdit, productName) {
        const serialNumber = await this.orm.call("stock.lot", "get_serial_number_available", [''], {product_name: productName});
        const { confirmed, payload } = await this.env.services.popup.add(EditListPopup, {
            title: _t("Lot/Serial Number(s) Required"),
            name: productName,
            isSingleItem: isAllowOnlyOneLot,
            array: packLotLinesToEdit,
            arraySerialNumber: serialNumber,
        });
        if (!confirmed) {
            return;
        }
        // Segregate the old and new packlot lines
        const modifiedPackLotLines = Object.fromEntries(
            payload.newArray.filter((item) => item.id).map((item) => [item.id, item.text])
        );
        const newPackLotLines = payload.newArray
            .filter((item) => !item.id)
            .map((item) => ({ lot_name: item.text }));

        return { modifiedPackLotLines, newPackLotLines };
    }

});

