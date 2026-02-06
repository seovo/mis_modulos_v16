# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class sale_order(models.Model):

    """Adds the fields for options of the customer order comment"""

    _inherit = "sale.order"
    _description = 'Sale Order'

    # customer_comment = fields.Text('Customer Order Comment', default="No comment")

    customer_comment = fields.Selection([('factura', 'Factura'), ('boleta', 'Boleta')], string='Tipo de comprobante')

    def _prepare_invoice(self):
        res = super(sale_order, self)._prepare_invoice()
        if self.customer_comment == 'factura':
            res['l10n_latam_document_type_id'] = 1
        else:
            res['l10n_latam_document_type_id'] = 3
        return res