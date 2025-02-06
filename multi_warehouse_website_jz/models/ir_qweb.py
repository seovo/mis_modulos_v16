# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.tools import is_html_empty, lazy
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request, route


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            if 'active_warehouse_id' in request.session:
                active_w = int(request.session['active_warehouse_id'])
                self.warehouse_id = active_w

        return res




class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    def _get_specific_rendering_values(self, processing_values):

        if 'active_warehouse_id' in request.session:
            active_w = int(request.session['active_warehouse_id'])
            self.sale_order_ids.warehouse_id = active_w
        """ Function to fetch the values of the payment gateway"""
        res = super()._get_specific_rendering_values(processing_values)


        return res


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"


    def _prepare_frontend_environment(self, values):
        """ Returns ir.qweb with context and update values with portal specific
            value (required to render portal layout template)
        """
        irQweb = super()._prepare_frontend_environment(values)

        #raise ValueError(values)

        #raise ValueError(values['res_company'].id)

        warehouses = irQweb.env['stock.warehouse'].sudo().search([('company_id','=',values['res_company'].id)])

        values.update(
            #is_html_empty=is_html_empty,
            warehouses=lazy(lambda: [lang for  lang in warehouses ])
        )

        if 'active_warehouse_id' in request.session:

            warehouse_active = irQweb.env['stock.warehouse'].sudo().search([('id', '=', int(request.session['active_warehouse_id']) )])
            values.update(warehouse=warehouse_active)

        else:
            request.session['active_warehouse_id'] = int(warehouses[0].id)

        for key in irQweb.env.context:
            if key not in values:
                values[key] = irQweb.env.context[key]


        #raise ValidationError(values['active_warehouse_id'])

        return irQweb
