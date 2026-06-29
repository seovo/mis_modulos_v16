/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.CheckDetails = publicWidget.Widget.extend({
    selector: '.checklist_jz',
    events: {
        //'change select[name="country_id"]': '_onCountryChange',
        'change input[type="checkbox"]': '_onInputChange',
        'change input[type="number"]': '_onInputChangeNumber',
        'click button[id="btnstate"]': '_onClickState',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        //alert('Iniciando');

        //this.$state = this.$('select[name="state_id"]');
        //this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
        //this._adaptAddressForm();

        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */

    _onClickState : function (ev) {



       var $item = $(ev.currentTarget);
       var PickingId = $item.data("id");
       var State = $item.data("state");


       jsonrpc('/picking/update/event', {
                    'picking_id': PickingId,
                    'state': State,
                    //'context': this.context,
                    //...this._getOptionalCombinationInfoParam($currentOptionalProduct),
        }).then((Data) => {
                    if (Data['total_done'] > 0 ){
                        if (Data['completed'] == true){
                           location.reload(true);

                        }else{
                           if (confirm('No Esta Completado toda la  lista, deseas confirmar ?')) {
                              jsonrpc('/picking/update/event', {
                                        'picking_id': PickingId,
                                        'state': State,
                                        'force': true
                              }).then((Datax) => {
                                 if (Datax['total_done'] > 0 ){
                                    if (Datax['completed'] == true){
                                         location.reload(true);

                                    }

                                 }else{
                                      alert('0 Cantidades Recepcionadas')

                                 }
                              });

                           }
                        }


                    }else{
                       alert('0 Cantidades Recepcionadas')

                    }

        });


    },

    _adaptAddressForm: function () {
        var $country = this.$('select[name="country_id"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
        this.$state.parent().toggle(nb >= 1);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */

    _onInputChangeNumber: function (ev) {
       var $item = $(ev.currentTarget);
       var $value = $item.val();
       console.log($value);

       var MoveId = $item.data("id");

       jsonrpc('/move/check/update', {
                    'move_id': MoveId,
                    'qty': $value,
                    'checked': null,
                    //'context': this.context,
                    //...this._getOptionalCombinationInfoParam($currentOptionalProduct),
                }).then((Data) => {
                    var search = `input[type="checkbox"][data-id="${MoveId}"]` ;
                    console.log(search);
                    var Cnumber = $(search);
                    console.log(Cnumber);
                    $item.val(Data['qty']);
                    if (Data['checked']){
                        $item.attr('disabled','disabled') ;
                        Cnumber.attr('checked','1') ;
                        window.location.reload();
                    }else{
                        $item.removeAttr('disabled') ;
                        Cnumber.removeAttr('checked') ;

                    }
                    //console.log(Data);
                    //this._onChangeCombination(ev, $currentOptionalProduct, combinationData);
                    //this._checkExclusions($currentOptionalProduct, childCombination, combinationData.parent_exclusions);
                });




    },

    _onInputChange: function (ev) {
        var $item = $(ev.currentTarget);
        var $value = $item.is(":checked") ;

        var MoveId = $item.data("id");

        var Qty =  null ;
        //var Qty = parseInt($currentOptionalProduct.find('input[name="add_qty"]').val()) ;

        jsonrpc('/move/check/update', {
                    'move_id': MoveId,
                    'qty': Qty,
                    'checked': $value,
                    //'context': this.context,
                    //...this._getOptionalCombinationInfoParam($currentOptionalProduct),
        }).then((Data) => {
                    //var search = `input[type="number"][data-id="${MoveId}"]` ;
                    //console.log(search);
                    //var Inumber = $(search);
                    // console.log(Inumber);

        });


    },
});