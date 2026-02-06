
odoo.define('culqi.payment', function (require) {
"use strict";


var ControlPanelMixin = require('web.ControlPanelMixin');
var Widget = require('web.Widget');
var core = require('web.core');


var StatementRenderer = Widget.extend(FieldManagerMixin, {
    template: 'cardPayment',

    events: {
    "click button.js_culqi_payment": "generate_payment",
    },

    generate_payment: function () {
        console.log("HOLAAAAAAAAAAAA33333");
    }

 });

});