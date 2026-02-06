/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { RPCError } from '@web/core/network/rpc_service';

//odoo.define('website_sale_custom.website_sale', function (require) {
//    'use strict';
//
//    var publicWidget = require('web.public.widget');
//    require('website_sale.website_sale');

publicWidget.registry.WebsiteSale.include({

    events:{
        'change #wsale_boleta': '_onChangeTipoComprobante',
        'change #wsale_factura': '_onChangeTipoComprobante',
        'change select[name="state_id"]': '_onChangeState',
        'change select[name="city_id"]': '_onChangeCity',
        'change select[name="l10n_pe_district"]': '_onChangeDistrict',
        'keyup #vat': '_onKeyupVat',
    },

    start() {
        const def = this._super(...arguments);
        this.$('select[name="state_id"]').change();
        return def;
    },

    _onChangeTipoComprobante: function (ev) {
        if (ev.target.value == 'boleta') {
            this.$('label[for="name"]')[0].innerHTML = 'Nombre';
        } else {
            this.$('label[for="name"]')[0].innerHTML = 'Razón Social';
        }
    },

    _onChangeState: function (ev) {
        // Departamento
        var selectCities = $("select[name='city_id']");
        var selectDistricts = $("select[name='l10n_pe_district']");
        selectCities.html('<option value="">Provincia...</option>');
        selectDistricts.html('<option value="">Distrito...</option>');
        if ($("#state_id").val() == '0') {
            selectCities.prop('disabled', true);
            selectDistricts.prop('disabled', true);
            $("#prov_sel").val('0');
            $("#dist_sel").val('0');
            return;
        } else {
            selectCities.prop('disabled', false);
            this._rpc({
                route: "/shop/state_infos/" + $("#state_id").val(),
                params: {},
            }).then(function (data) {
                selectCities.html('<option value="0">Provincia...</option>');
                _.each(data.cities, function (x) {
                    let selected = false;
                    if (x[0] == $("#prov_sel").val()) {
                        selected = true;
                    }
                    var opt = $('<option>').text(x[1]).attr('value', x[0]).prop('selected', selected);
                    selectCities.append(opt);
                });
                selectCities.change();
            });
        }
    },

    _onChangeCity: function (ev) {
        // Provincia
        $("#prov_sel").val($("#city_id").val());
        var selectDistricts = $("select[name='l10n_pe_district']");
        selectDistricts.html('<option value="">Distrito...</option>');
        if ($("#city_id").val() == '0') {
            selectDistricts.prop('disabled', true);
            $("#prov_sel").val('0');
            $("#dist_sel").val('0');
            $("input[name='city']").val('');
            return;
        } else {
            let ciudad = $("#city_id").find(':selected').text();
            $("input[name='city']").val(ciudad);
            selectDistricts.prop('disabled', false);
            this._rpc({
                route: "/shop/city_infos/" + $("#prov_sel").val(),
                params: {},
            }).then(function (data) {
                selectDistricts.html('<option value="0">Distrito...</option>');
                _.each(data.districts, function (x) {
                    let selected = false;
                    if (x[0] == $("#dist_sel").val()) {
                        selected = true;
                    }
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2])
                        .prop('selected', selected);
                    selectDistricts.append(opt);
                });
                selectDistricts.change();
            });
        }
    },

    _onChangeDistrict: function (ev) {
        // Distrito
        $("#dist_sel").val($("#l10n_pe_district").val());
        if ($("#l10n_pe_district").val() == '0') {
            $("input[name='zip']").val('');
        } else {
            $("input[name='zip']").val($("#l10n_pe_district").find(':selected').attr('data-code'));
        }
    },

    _onKeyupVat: function (ev) {
        if ($("#l10n_latam_identification_type_id").find(':selected').attr('data') == '6' && $("#vat").val().length == 11) {
            this._rpc({
                route: "/shop/consulta_ruc",
                params: {
                    vat: $("#vat").val(),
                    country: $("#country_id").val(),
                },
            }).then(function (data) {
                console.log(data);
                if (!Object.hasOwn(data, 'error')) {
                    if (Object.hasOwn(data, 'name')) {
                        $("input[name='name']").val(data.name);
                    }
                    if (Object.hasOwn(data, 'street')) {
                        $("input[name='street']").val(data.street);
                    }
                    if (Object.hasOwn(data, 'l10n_pe_district')) {
                        $("#dist_sel").val(data.l10n_pe_district);
                    }
                    if (Object.hasOwn(data, 'city_id')) {
                        $("#prov_sel").val(data.city_id);
                    }
                    if (Object.hasOwn(data, 'state_id')) {
                        $("select[name='state_id']").val(data.state_id);
                        $("select[name='state_id']").change();
                    }
                }
            });
        }
    },

});

//});