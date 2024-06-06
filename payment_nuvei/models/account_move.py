# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_line_ids', 'invoice_line_ids.tax_ids')
    def _compute_tax_percentage(self):
        """
        Calcula el campo tax_percentage:
        - Si alguna de las lineas tiene impuestos mayor que cero entonces toma ese valor, ej. 12
        - Si no hay lineas de impuestos mayor que cero entonces es 0
        Calcula el campo amount_iva_taxable: Este campo esla base imponible de los impuestos diferenctes de cero
        """
        for invoice_id in self:
            line_tax_ids = sorted(invoice_id.invoice_line_ids.mapped('tax_ids'), key=lambda t: t.amount, reverse=True)
            if not line_tax_ids:
                invoice_id.tax_percentage = 0.0
                invoice_id.amount_iva_taxable = invoice_id.amount_untaxed
            else:
                invoice_id.tax_percentage = line_tax_ids[0].amount
                invoice_id.amount_iva_taxable = invoice_id.amount_untaxed - sum(invoice_id.invoice_line_ids.filtered(
                    lambda line: not sum(line.tax_ids.mapped('amount'))
                ).mapped('price_subtotal'))

    tax_percentage = fields.Float(
        string='Tax percentage',
        compute='_compute_tax_percentage',
        help='Field to get tax percentage of sale order based on lines tax.'
    )
    amount_iva_taxable = fields.Monetary(
        string='Iva taxable', compute='_compute_tax_percentage'
    )
