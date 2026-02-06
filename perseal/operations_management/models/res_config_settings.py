# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_partner_category_cedente_id = fields.Many2one(
        readonly=False,
        string='Cedente',
        related='company_id.company_partner_category_cedente_id'
    )
    company_partner_category_deudor_id = fields.Many2one(
        readonly=False,
        string='Deudor',
        related='company_id.company_partner_category_deudor_id'
    )
    company_partner_category_proveedor_id = fields.Many2one(
        readonly=False,
        string='Proveedor',
        related='company_id.company_partner_category_proveedor_id'
    )
    company_partner_category_beneficiario_id = fields.Many2one(
        readonly=False,
        string='Beneficiario',
        related='company_id.company_partner_category_beneficiario_id'
    )
    company_partner_category_titular_id = fields.Many2one(
        readonly=False,
        string='Titular',
        related='company_id.company_partner_category_titular_id'
    )
