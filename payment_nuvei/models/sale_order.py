# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, exceptions, _
from odoo.tools import float_compare
from .nuvei_api import NuveiAPI
from odoo.http import request


STATUS_MAP = {'success': 'cancel', 'failure': 'done', 'pending': 'pending'}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line', 'order_line.tax_id')
    def _compute_tax_percentage(self):
        """
        Calcula el campo tax_percentage:
        - Si alguna de las lineas tiene impuestos mayor que cero entonces toma ese valor, ej. 12
        - Si no hay lineas de impuestos mayor que cero entonces es 0
        Calcula el campo amount_iva_taxable: Este campo esla base imponible de los impuestos diferenctes de cero
        """
        for order_id in self:
            line_tax_ids = sorted(order_id.order_line.mapped('tax_id'), key=lambda t: t.amount, reverse=True)
            if not line_tax_ids:
                order_id.tax_percentage = 0.0
                order_id.amount_iva_taxable = order_id.amount_untaxed
            else:
                order_id.tax_percentage = line_tax_ids[0].amount
                order_id.amount_iva_taxable = order_id.amount_untaxed - sum(order_id.order_line.filtered(
                    lambda line: not sum(line.tax_id.mapped('amount'))
                ).mapped('price_subtotal'))

    tax_percentage = fields.Float(
        string='Tax percentage',
        compute='_compute_tax_percentage',
        help='Field to get tax percentage of sale order based on lines tax.'
    )
    amount_iva_taxable = fields.Monetary(
        string='Iva taxable', compute='_compute_tax_percentage'
    )

    def ecommerce_refund(self):
        """
        Make an ecommerce refund over an sale order. Use transaction state
        to know if order is refundable
        """
        self.ensure_one()
        tx = self.transaction_ids.filtered(lambda t: t.state == 'done')
        if not tx:
            raise exceptions.ValidationError(_('To refund this order is mandatory a transaction in done state.'))
        if len(tx) > 1:
            raise exceptions.ValidationError(_('This order has been paid more than once. Please contact with account manager.'))
        api = NuveiAPI(tx.provider_id)
        response = api.create_refund(tx.provider_reference)
        transaction_status = response.get('status', '')
        transaction_details = response.get('detail', '')
        state = STATUS_MAP.get(transaction_status, 'done')
        res = {
            'state': state,
            'state_message': '%s\nRefund: %s' % (tx.state_message or '', transaction_details)
        }
        return tx.write(res)


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False,
                       update_pricelist=False):
        """
        Herencia para mantener actualizado el campo 'last_website_so_id'
        y en caso de error se mantenga en el carro la orden actual
        """
        sale_order_id = super(Website, self).sale_get_order(
            force_create=force_create,
            update_pricelist=update_pricelist
        )
        public_partner = self.env.ref('base.public_partner')
        if sale_order_id and sale_order_id.partner_id != public_partner:
            if not sale_order_id.partner_id.last_website_so_id or \
                    sale_order_id.partner_id.last_website_so_id.id != sale_order_id.id:
                sale_order_id.partner_id.write(
                    {'last_website_so_id': sale_order_id.id}
                )
        return sale_order_id
