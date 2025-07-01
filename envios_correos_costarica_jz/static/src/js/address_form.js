/** @odoo-module */

import { WebsiteSale } from '@website_sale/js/website_sale';


WebsiteSale.include({
    /**
     * Toggles the add to cart button depending on the possibility of the
     * current combination.
     *
     * @override
     */

     events: Object.assign({}, WebsiteSale.prototype.events, {
        'change select[name="state_id"]': '_onChangeStateCr',
        'change select[name="county_id"]': '_onChangeCountyCr',

     }),

     start: function () {

         this.elementCantons = document.querySelector("select[name='county_id']");
         this.elementDistricts = document.querySelector("select[name='district_id']");

         //this._onChangeStateCr();
         //this._onChangeCountyCr();

         return this._super.apply(this, arguments);

     },

     _onChangeCountry: function (ev) {
         var res = this._super.apply(this, arguments);
         //this._onChangeStateCr();
         console.log('kii');
         //var state  = $("select[name='state_id']");
         //state.change();
         //this._onChangeCountyCr();

         return res ;

     },

     _changeOptionCr: function (selectCheck, rpcRoute, place, selectElement) {
        if (!selectCheck) {
            return;
        }
        return this.rpc(rpcRoute, {
        }).then((data) => {
            //if (this.isPeruvianCompany) {
            if (1 == 1) {
                if (data[place]?.length) {
                    selectElement.innerHTML = "<option value='0'>Seleccione...</option>";
                    //selectElement.innerHTML = "";
                    data[place].forEach((item) => {
                        let opt = document.createElement("option");
                        opt.textContent = item[1];
                        opt.value = item[0];
                        opt.setAttribute("data-code", item[2]);
                        selectElement.appendChild(opt);
                    });
                    selectElement.parentElement.style.display = "block";
                } else {
                    selectElement.value = "";
                    selectElement.parentElement.style.display = "none";
                }
            }
        });
    },

     _onChangeCountyCr: function (ev) {
         this._onChangeCanton();
     },



    _onChangeStateCr: function (ev) {
        //console.log('KEUUUU');
        //console.log(ev.target.value);

        const state = document.querySelector("select[name='state_id']").value;
        if (state == 0){
           return
        }
        const rpcRoute = `/shop/state_infos_cr/${state}`;
        return this._changeOptionCr(state, rpcRoute, "cantons", this.elementCantons).then(() => this._onChangeCanton()) ;

    },

    _onChangeCanton: function () {

            const city = this.elementCantons.value;
            if (city == 0){
                return
            }
            const rpcRoute = `/shop/canton_infos/${city}`;
            return this._changeOptionCr(city, rpcRoute, "districts", this.elementDistricts) ;


    },

});


