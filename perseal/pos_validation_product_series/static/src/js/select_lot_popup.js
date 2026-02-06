/** @odoo-module */

import { EditListPopup } from "@point_of_sale/app/store/select_lot_popup/select_lot_popup";
import { patch } from "@web/core/utils/patch";

patch(EditListPopup.prototype, {
    async confirm() {

        if (this.props.arraySerialNumber.includes( this.getPayload().newArray[0].text)){
            this.props.close({ confirmed: true, payload: await this.getPayload() });
        }else{
            const stringSerialNumber = this.props.arraySerialNumber.join(', ');
            window.alert('El número de serie/lote "' + this.getPayload().newArray[0].text + '" no existe para el producto ' + this.props.name + '\nTiene disponible las series ' +stringSerialNumber);
        }
    }
});